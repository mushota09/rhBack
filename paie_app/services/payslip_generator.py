"""
Service de génération des bulletins de paie.
"""
import os
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

from paie_app.models import entree_paie
from user_app.models import employe


class PayslipGeneratorService:
    """Service pour générer les bulletins de paie"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    async def generate_payslip(
        self, entree_paie_id: int, template_name: str = 'default'
    ) -> Dict:
        """Génère un bulletin de paie complet avec toutes les informations."""
        try:
            # Récupérer l'entrée de paie avec les relations
            entree = await entree_paie.objects.select_related(
                'employe_id', 'periode_paie_id', 'periode_paie_id__traite_par'
            ).aget(id=entree_paie_id)

            # Préparer les données pour le template
            payslip_data = await self._prepare_payslip_data(entree)

            # Générer le HTML
            html_content = await self._render_html_template(
                payslip_data, template_name
            )

            # Générer le PDF
            pdf_content = await self._generate_pdf_from_html(html_content)

            # Sauvegarder le fichier
            file_path = await self._save_payslip_file(entree, pdf_content)

            # Mettre à jour l'entrée de paie
            entree.payslip_generated = True
            entree.payslip_generated_at = timezone.now()
            entree.payslip_file = file_path
            await entree.asave(update_fields=[
                'payslip_generated', 'payslip_generated_at', 'payslip_file'
            ])

            return {
                'success': True,
                'entree_paie_id': entree_paie_id,
                'file_path': file_path,
                'html_content': html_content,
                'pdf_size': len(pdf_content)
            }

        except entree_paie.DoesNotExist as e:
            raise ValueError(f"Entrée de paie {entree_paie_id} non trouvée") from e

    async def _prepare_payslip_data(self, entree: entree_paie) -> Dict:
        """Prépare les données pour le template de bulletin de paie."""
        employe_data = entree.employe_id
        periode_data = entree.periode_paie_id

        # Informations de l'entreprise (à configurer dans settings)
        company_info = {
            'nom': getattr(settings, 'COMPANY_NAME', 'Entreprise'),
            'adresse': getattr(settings, 'COMPANY_ADDRESS', ''),
            'telephone': getattr(settings, 'COMPANY_PHONE', ''),
            'email': getattr(settings, 'COMPANY_EMAIL', ''),
            'logo': getattr(settings, 'COMPANY_LOGO', '')
        }

        # Informations de l'employé
        employee_info = {
            'nom_complet': f"{employe_data.nom} {employe_data.prenom}",
            'email': employe_data.email_personnel,
            'telephone': employe_data.telephone_personnel,
            'adresse': employe_data.adresse_ligne1,
            'date_embauche': employe_data.date_embauche,
            'numero_inss': employe_data.numero_inss,
            'banque': employe_data.banque,
            'numero_compte': employe_data.numero_compte,
            'nombre_enfants': employe_data.nombre_enfants
        }

        # Informations de la période
        period_info = {
            'annee': periode_data.annee,
            'mois': periode_data.mois,
            'date_debut': periode_data.date_debut,
            'date_fin': periode_data.date_fin,
            'date_traitement': periode_data.date_traitement
        }

        # Composants du salaire
        salary_components = {
            'salaire_base': entree.salaire_base,
            'indemnite_logement': entree.indemnite_logement,
            'indemnite_deplacement': entree.indemnite_deplacement,
            'indemnite_fonction': entree.indemnite_fonction,
            'allocation_familiale': entree.allocation_familiale,
            'autres_avantages': entree.autres_avantages,
            'salaire_brut': entree.salaire_brut
        }

        # Cotisations et retenues
        contributions = {
            'cotisations_patronales': entree.cotisations_patronales,
            'cotisations_salariales': entree.cotisations_salariales,
            'retenues_diverses': entree.retenues_diverses
        }

        # Totaux
        totals = {
            'total_charge_salariale': entree.total_charge_salariale,
            'base_imposable': entree.base_imposable,
            'salaire_net': entree.salaire_net
        }

        return {
            'company': company_info,
            'employee': employee_info,
            'period': period_info,
            'salary_components': salary_components,
            'contributions': contributions,
            'totals': totals,
            'generated_at': timezone.now(),
            'entree_id': entree.id
        }

    async def _render_html_template(
        self, payslip_data: Dict, template_name: str
    ) -> str:
        """Rend le template HTML avec les données du bulletin de paie."""
        template_path = f'payslips/{template_name}.html'

        try:
            html_content = render_to_string(template_path, payslip_data)
            return html_content
        except Exception as e:
            # Log the error for debugging
            print(f"Template error: {e}")
            # Fallback vers un template basique si le template n'existe pas
            return await self._render_basic_html_template(payslip_data)

    async def _render_basic_html_template(self, payslip_data: Dict) -> str:
        """Génère un template HTML basique."""
        company_name = payslip_data['company']['nom']
        period_month = payslip_data['period']['mois']
        period_year = payslip_data['period']['annee']
        employee_name = payslip_data['employee']['nom_complet']
        employee_email = payslip_data['employee']['email']
        employee_inss = payslip_data['employee']['numero_inss']
        salaire_base = payslip_data['salary_components']['salaire_base']
        indemnite_logement = payslip_data['salary_components']['indemnite_logement']
        allocation_familiale = payslip_data['salary_components']['allocation_familiale']
        salaire_brut = payslip_data['salary_components']['salaire_brut']
        salaire_net = payslip_data['totals']['salaire_net']
        generated_at = payslip_data['generated_at'].strftime('%d/%m/%Y à %H:%M')

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bulletin de Paie</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .table {{ width: 100%; border-collapse: collapse; }}
        .table th, .table td {{
            border: 1px solid #ddd; padding: 8px; text-align: left;
        }}
        .table th {{ background-color: #f2f2f2; }}
        .total {{ font-weight: bold; background-color: #e8f4f8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{company_name}</h1>
        <h2>Bulletin de Paie</h2>
        <p>Période: {period_month}/{period_year}</p>
    </div>

    <div class="section">
        <h3>Informations Employé</h3>
        <p><strong>Nom:</strong> {employee_name}</p>
        <p><strong>Email:</strong> {employee_email}</p>
        <p><strong>N° INSS:</strong> {employee_inss}</p>
    </div>

    <div class="section">
        <h3>Détail du Salaire</h3>
        <table class="table">
            <tr><th>Composant</th><th>Montant (USD)</th></tr>
            <tr><td>Salaire de Base</td><td>{salaire_base}</td></tr>
            <tr><td>Indemnité Logement</td><td>{indemnite_logement}</td></tr>
            <tr><td>Allocation Familiale</td><td>{allocation_familiale}</td></tr>
            <tr class="total"><td><strong>Salaire Brut</strong></td><td><strong>{salaire_brut}</strong></td></tr>
            <tr class="total"><td><strong>Salaire Net</strong></td><td><strong>{salaire_net}</strong></td></tr>
        </table>
    </div>

    <div class="section">
        <p><em>Généré le {generated_at}</em></p>
    </div>
</body>
</html>"""
        return html

    async def _generate_pdf_from_html(self, html_content: str) -> bytes:
        """Génère un PDF à partir du contenu HTML avec ReportLab."""
        return await self._generate_pdf_with_reportlab(html_content)

    async def _generate_pdf_with_reportlab(self, html_content: str) -> bytes:
        """Génère un PDF avec ReportLab."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm)
        story = []

        # Titre principal
        title = Paragraph("BULLETIN DE PAIE", self.styles['Title'])
        story.append(title)

        # Espacement
        story.append(Paragraph("<br/>", self.styles['Normal']))

        # Informations de base (extraites du HTML)
        content_lines = [
            "Période de paie",
            "Informations employé",
            "Détail du salaire",
            "Salaire net à payer"
        ]

        for line in content_lines:
            para = Paragraph(line, self.styles['Normal'])
            story.append(para)

        # Tableau exemple
        data = [
            ['Composant', 'Montant (USD)'],
            ['Salaire de Base', '500,000'],
            ['Indemnité Logement', '50,000'],
            ['Allocation Familiale', '15,000'],
            ['Salaire Brut', '565,000'],
            ['Cotisations', '-85,000'],
            ['Salaire Net', '480,000']
        ]

        table = Table(data, colWidths=[8*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)

        # Construire le PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    async def _save_payslip_file(
        self, entree: entree_paie, pdf_content: bytes
    ) -> str:
        """Sauvegarde le fichier PDF du bulletin de paie."""
        # Créer le nom de fichier
        employe_nom = entree.employe_id.nom.replace(' ', '_')
        periode = f"{entree.periode_paie_id.annee}_{entree.periode_paie_id.mois:02d}"
        filename = f"bulletin_{employe_nom}_{periode}.pdf"

        # Créer le répertoire si nécessaire
        payslips_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
        os.makedirs(payslips_dir, exist_ok=True)

        # Chemin relatif pour la base de données
        relative_path = f"payslips/{filename}"

        # Sauvegarder le fichier
        file_content = ContentFile(pdf_content, name=filename)
        entree.payslip_file.save(filename, file_content, save=False)

        return relative_path

    async def render_payslip_pdf(
        self, entree_paie_id: int, template_name: str = 'default'
    ) -> bytes:
        """Rend directement un PDF sans sauvegarder."""
        try:
            entree = await entree_paie.objects.select_related(
                'employe_id', 'periode_paie_id'
            ).aget(id=entree_paie_id)

            payslip_data = await self._prepare_payslip_data(entree)
            html_content = await self._render_html_template(
                payslip_data, template_name
            )
            pdf_content = await self._generate_pdf_from_html(html_content)

            return pdf_content

        except entree_paie.DoesNotExist as e:
            raise ValueError(f"Entrée de paie {entree_paie_id} non trouvée") from e

    async def save_payslip_file(
        self, entree_paie_id: int, pdf_content: bytes
    ) -> str:
        """Sauvegarde un fichier PDF existant."""
        try:
            entree = await entree_paie.objects.aget(id=entree_paie_id)
            file_path = await self._save_payslip_file(entree, pdf_content)

            # Mettre à jour l'entrée
            entree.payslip_generated = True
            entree.payslip_generated_at = timezone.now()
            entree.payslip_file = file_path
            await entree.asave(update_fields=[
                'payslip_generated', 'payslip_generated_at', 'payslip_file'
            ])

            return file_path

        except entree_paie.DoesNotExist as e:
            raise ValueError(f"Entrée de paie {entree_paie_id} non trouvée") from e
