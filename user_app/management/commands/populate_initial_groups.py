from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from user_app.models import Group, Permission, GroupPermission


class Command(BaseCommand):
    help = 'Populate initial groups, permissions, and group permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of all data',
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            self.stdout.write(sel
     """Create the 21 predefined groups"""
        groups_data = [
            ("ADM", "Administrateur", "Administrateur système avec accès complet"),
            ("AP", "Analyste des Projets", "Analyste responsable du suivi des projets"),
            ("AI", "Auditeur interne", "Auditeur interne responsable du contrôle"),
            ("CSE", "Chargé du Suivi-Evaluation", "Responsable du suivi et évaluation"),
            ("CH", "Chauffeur", "Chauffeur responsable du transport"),
            ("CS", "Chef de service", "Chef de service d'une unité organisationnelle"),
            ("CSFP", "Chef Service Financement Projets", "Chef du service de financement"),
            ("CCI", "Chef du contrôle interne", "Chef du service de contrôle interne"),
            ("CM", "Comptable", "Comptable responsable de la gestion financière"),
            ("DIR", "Directeur/Directrice", "Directeur avec autorité de direction"),
            ("GS", "Gestionnaire de Stock", "Gestionnaire de la gestion des stocks"),
            ("IT", "Informaticien", "Informaticien des systèmes informatiques"),
            ("JR", "Juriste", "Juriste responsable des questions juridiques"),
            ("LG", "Logisticien", "Logisticien responsable de la logistique"),
            ("PL", "Planton", "Planton responsable de l'accueil et sécurité"),
            ("PCA", "Président commission d'appel", "Président de la commission d'appel"),
            ("PCR", "Président commission réception", "Président commission réception"),
            ("PCDR", "Président commission recrutement", "Président commission recrutement"),
            ("RAF", "Responsable Administratif et Financier", "Responsable administratif"),
            ("RRH", "Responsable Ressources Humaines", "Responsable des ressources humaines"),
            ("SEC", "Secrétaire", "Secrétaire responsable du support administratif"),
        ]

        created_count = 0
        for code, name, description in groups_data:
            group, created = Group.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description, 'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created group: {code} - {name}')

        self.stdout.write(self.style.SUCCESS(f'Groups: {created_count} created'))

    def create_permissions(self):
        """Create system permissions"""
        from user_app.models import employe, contrat, document, User, audit_log
        from paie_app.models import periode_paie, retenue_employe
        from conge_app.models import demande_conge

        content_types = {
            'employee': ContentType.objects.get_for_model(employe),
            'contract': ContentType.objects.get_for_model(contrat),
            'payroll': ContentType.objects.get_for_model(periode_paie),
            'leave': ContentType.objects.get_for_model(demande_conge),
            'deduction': ContentType.objects.get_for_model(retenue_employe),
            'document': ContentType.objects.get_for_model(document),
            'user_management': ContentType.objects.get_for_model(User),
            'audit': ContentType.objects.get_for_model(audit_log),
        }

        permissions_data = [
            ("employee.create", "Create Employee", "employee", "CREATE"),
            ("employee.read", "Read Employee", "employee", "READ"),
            ("employee.update", "Update Employee", "employee", "UPDATE"),
            ("employee.delete", "Delete Employee", "employee", "DELETE"),
            ("contract.create", "Create Contract", "contract", "CREATE"),
            ("contract.read", "Read Contract", "contract", "READ"),
            ("contract.update", "Update Contract", "contract", "UPDATE"),
            ("contract.delete", "Delete Contract", "contract", "DELETE"),
            ("payroll.create", "Create Payroll", "payroll", "CREATE"),
            ("payroll.read", "Read Payroll", "payroll", "READ"),
            ("payroll.update", "Update Payroll", "payroll", "UPDATE"),
            ("payroll.delete", "Delete Payroll", "payroll", "DELETE"),
            ("payroll.approve", "Approve Payroll", "payroll", "UPDATE"),
            ("leave.create", "Create Leave", "leave", "CREATE"),
            ("leave.read", "Read Leave", "leave", "READ"),
            ("leave.update", "Update Leave", "leave", "UPDATE"),
            ("leave.delete", "Delete Leave", "leave", "DELETE"),
            ("leave.approve", "Approve Leave", "leave", "UPDATE"),
            ("deduction.create", "Create Deduction", "deduction", "CREATE"),
            ("deduction.read", "Read Deduction", "deduction", "READ"),
            ("deduction.update", "Update Deduction", "deduction", "UPDATE"),
            ("deduction.delete", "Delete Deduction", "deduction", "DELETE"),
            ("document.create", "Create Document", "document", "CREATE"),
            ("document.read", "Read Document", "document", "READ"),
            ("document.update", "Update Document", "document", "UPDATE"),
            ("document.delete", "Delete Document", "document", "DELETE"),
            ("user_management.create", "Create User Management", "user_management", "CREATE"),
            ("user_management.read", "Read User Management", "user_management", "READ"),
            ("user_management.update", "Update User Management", "user_management", "UPDATE"),
            ("user_management.delete", "Delete User Management", "user_management", "DELETE"),
            ("audit.read", "Read Audit", "audit", "READ"),
            ("system.create", "Create System", "user_management", "CREATE"),
            ("system.read", "Read System", "user_management", "READ"),
            ("system.update", "Update System", "user_management", "UPDATE"),
            ("system.delete", "Delete System", "user_management", "DELETE"),
            ("report.read", "Read Reports", "audit", "READ"),
        ]

        created_count = 0
        for codename, name, resource, action in permissions_data:
            content_type = content_types.get(resource)
            if content_type:
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    defaults={
                        'name': name,
                        'content_type': content_type,
                        'resource': resource,
                        'action': action,
                        'description': f'Permission to {action.lower()} {resource}'
                    }
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Permissions: {created_count} created'))

    def create_group_permissions(self):
        """Create group permission assignments"""
        groups = {group.code: group for group in Group.objects.all()}
        permissions = {perm.codename: perm for perm in Permission.objects.all()}

        # Define hierarchical permissions for key groups
        group_permissions = {
            'ADM': [  # Full access
                'employee.create', 'employee.read', 'employee.update', 'employee.delete',
                'contract.create', 'contract.read', 'contract.update', 'contract.delete',
                'payroll.create', 'payroll.read', 'payroll.update', 'payroll.delete', 'payroll.approve',
                'leave.create', 'leave.read', 'leave.update', 'leave.delete', 'leave.approve',
                'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
                'document.create', 'document.read', 'document.update', 'document.delete',
                'user_management.create', 'user_management.read', 'user_management.update', 'user_management.delete',
                'audit.read', 'system.create', 'system.read', 'system.update', 'system.delete', 'report.read'
            ],
            'DIR': [  # Director access
                'employee.create', 'employee.read', 'employee.update', 'employee.delete',
                'contract.create', 'contract.read', 'contract.update', 'contract.delete',
                'payroll.create', 'payroll.read', 'payroll.update', 'payroll.delete', 'payroll.approve',
                'leave.create', 'leave.read', 'leave.update', 'leave.delete', 'leave.approve',
                'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
                'document.create', 'document.read', 'document.update', 'document.delete',
                'user_management.read', 'user_management.update', 'audit.read', 'report.read'
            ],
            'RRH': [  # HR Manager
                'employee.create', 'employee.read', 'employee.update', 'employee.delete',
                'contract.create', 'contract.read', 'contract.update', 'contract.delete',
                'payroll.create', 'payroll.read', 'payroll.update', 'payroll.delete',
                'leave.create', 'leave.read', 'leave.update', 'leave.delete', 'leave.approve',
                'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
                'document.create', 'document.read', 'document.update', 'document.delete',
                'user_management.create', 'user_management.read', 'user_management.update', 'user_management.delete',
                'audit.read', 'report.read'
            ],
            'RAF': [  # Administrative and Financial Manager
                'employee.read', 'contract.read',
                'payroll.create', 'payroll.read', 'payroll.update', 'payroll.delete', 'payroll.approve',
                'leave.read', 'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
                'document.read', 'report.read'
            ],
            'CM': [  # Accountant
                'employee.read', 'contract.read', 'payroll.create', 'payroll.read', 'payroll.update',
                'deduction.read', 'document.read', 'report.read'
            ],
            'AI': [  # Internal Auditor
                'employee.read', 'contract.read', 'payroll.read', 'leave.read',
                'deduction.read', 'document.read', 'audit.read', 'report.read'
            ],
            'IT': [  # IT Specialist
                'employee.read', 'contract.read', 'payroll.read', 'leave.read', 'deduction.read', 'document.read',
                'user_management.create', 'user_management.read', 'user_management.update', 'user_management.delete',
                'system.create', 'system.read', 'system.update', 'system.delete'
            ],
            'CS': [  # Service Manager
                'employee.read', 'employee.update', 'contract.read', 'contract.update',
                'payroll.read', 'payroll.update', 'leave.read', 'leave.update', 'leave.approve',
                'deduction.read', 'deduction.update', 'document.read', 'document.update', 'report.read'
            ],
            'SEC': [  # Secretary
                'employee.read', 'contract.read', 'payroll.read',
                'leave.create', 'leave.read', 'document.create', 'document.read', 'document.update'
            ]
        }

        created_count = 0
        for group_code, permission_codes in group_permissions.items():
            group = groups.get(group_code)
            if not group:
                continue

            for permission_code in permission_codes:
                permission = permissions.get(permission_code)
                if not permission:
                    continue

                group_permission, created = GroupPermission.objects.get_or_create(
                    group=group, permission=permission, defaults={'granted': True}
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Group permissions: {created_count} created'))
