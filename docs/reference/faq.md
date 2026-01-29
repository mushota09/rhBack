# Questions Fréquemment Posées (FAQ)

Cette section répond aux questions les plus courantes concernant l'utilisation du système de paie.

## Questions Générales

### Q: Comment démarrer avec le système de paie ?

**R:** Suivez ces étapes :
1. Consultez le [Guide de Démarrage Rapide](../user-guides/quick-start.md)
2. Assurez-vous d'avoir les permissions appropriées
3. Vérifiez que les employés et contrats sont créés
4. Configurez les [Paramètres de Paie](../configuration/payroll-parameters.md)
5. Créez votre première période de paie

### Q: Quelle est la différence entre finaliser et approuver une période ?

**R:**
- **Finaliser** : Verrouille les calculs et empêche les modifications. La période peut encore être "dé-finalisée" si nécessaire.
- **Approuver** : Validation finale et définitive. Aucune modification n'est possible après approbation.

### Q: Puis-je traiter plusieurs périodes simultanément ?

**R:** Non, le système ne permet de traiter qu'une seule période à la fois pour éviter les conflits de données et assurer la cohérence des calculs.

## Gestion des Périodes

### Q: Pourquoi ne puis-je pas créer une période pour un mois donné ?

**R:** Vérifiez ces points :
- Une période existe peut-être déjà pour ce mois/année
- Vous n'avez peut-être pas les permissions nécessaires
- Le mois/année pourrait être dans le futur lointain (limite système)

#
ment
4. Si le problème persiste, consultez les [logs système](../administration/troubleshooting.md)

## Calculs Salariaux

### Q: Comment sont calculées les cotisations INSS ?

**R:**
- **Pension** : 6% patronal, 3% salarial (plafond 27,000 USD)
- **Risque** : 6% patronal, 1.5% salarial (plafond 2,400 USD)
- Le plafond s'applique à la base de calcul, pas au montant de la cotisation

### Q: Pourquoi le salaire net est-il négatif ?

**R:** Cela peut arriver si :
- Les retenues dépassent le salaire brut
- Il y a une erreur dans les paramètres de calcul
- Les données contractuelles sont incorrectes

**Solution :** Vérifiez les retenues et les paramètres, ajustez si nécessaire.

### Q: Comment fonctionne le calcul de l'IRE ?

**R:** L'IRE utilise un barème progressif :
- 0 à 150,000 USD : 0%
- 150,001 à 300,000 USD : 20%
- Plus de 300,000 USD : 30%

La base imposable = salaire brut - cotisations salariales.

### Q: Les indemnités sont-elles soumises aux cotisations ?

**R:** Oui, toutes les indemnités (logement, déplacement, fonction) sont incluses dans le salaire brut et soumises aux cotisations sociales et à l'IRE.

## Retenues et Déductions

### Q: Comment créer une retenue récurrente ?

**R:**
1. Allez dans **Paie > Retenues**
2. Cliquez sur **Nouvelle Retenue**
3. Cochez "Est récurrente"
4. Définissez les dates de début et fin
5. Le système appliquera automatiquement la retenue chaque mois

### Q: Puis-je modifier une retenue en cours ?

**R:** Oui, mais les modifications ne s'appliquent qu'aux futures déductions. Les déductions déjà effectuées ne sont pas modifiées.

### Q: Comment arrêter une retenue avant son terme ?

**R:** Utilisez la fonction "Désactiver" dans la liste des retenues. Spécifiez la date d'arrêt et la raison.

### Q: Quelle est la limite maximale de retenues ?

**R:** Par défaut, les retenues ne peuvent pas dépasser 50% du salaire brut. Cette limite peut être configurée par l'administrateur.

## Bulletins de Paie

### Q: Comment générer des bulletins pour tous les employés ?

**R:**
1. Allez dans la période traitée
2. Cliquez sur "Générer Bulletins"
3. Sélectionnez le template souhaité
4. Lancez la génération (traitement asynchrone)

### Q: Puis-je personnaliser le format des bulletins ?

**R:** Oui, trois templates sont disponibles :
- **Simple** : Format basique
- **Standard** : Format complet avec détails
- **Premium** : Format professionnel avec logo

### Q: Comment télécharger un bulletin individuel ?

**R:**
1. Allez dans **Paie > Entrées de Paie**
2. Trouvez l'employé concerné
3. Cliquez sur l'icône PDF ou "Télécharger Bulletin"

### Q: Que faire si la génération de bulletin échoue ?

**R:**
- Vérifiez que les calculs sont corrects
- Assurez-vous que le template existe
- Consultez les logs d'erreur
- Essayez de régénérer le bulletin individuel

## Performance et Technique

### Q: Combien de temps prend le traitement d'une période ?

**R:** Cela dépend du nombre d'employés :
- 50 employés : ~2-3 minutes
- 100 employés : ~5-7 minutes
- 500 employés : ~20-30 minutes

### Q: Le système peut-il gérer de gros volumes ?

**R:** Oui, le système est conçu pour :
- Traitement asynchrone par lots
- Calculs parallèles
- Optimisation des requêtes de base de données
- Cache des données de référence

### Q: Comment améliorer les performances ?

**R:**
- Utilisez le traitement asynchrone
- Configurez correctement le cache Redis
- Optimisez la base de données
- Traitez pendant les heures creuses

## Sécurité et Permissions

### Q: Qui peut créer des périodes de paie ?

**R:** Seuls les utilisateurs avec le rôle "RH" ou "ADMIN" peuvent créer et traiter des périodes de paie.

### Q: Comment sont sécurisées les APIs ?

**R:**
- Authentification JWT obligatoire
- Permissions basées sur les rôles
- Chiffrement HTTPS
- Audit de toutes les opérations

### Q: Puis-je limiter l'accès à certaines données ?

**R:** Oui, les permissions peuvent être configurées au niveau :
- Utilisateur
- Rôle
- Service/Département
- Type d'opération

## Intégration et APIs

### Q: Comment intégrer le système avec notre ERP ?

**R:**
1. Utilisez les [APIs REST](api-reference.md) documentées
2. Configurez l'authentification JWT
3. Implémentez les webhooks pour les notifications
4. Testez avec l'environnement de développement

### Q: Quels formats d'export sont supportés ?

**R:**
- **Excel** : Pour l'analyse de données
- **PDF** : Pour les rapports officiels
- **JSON** : Pour l'intégration API
- **CSV** : Pour l'import dans d'autres systèmes

### Q: Comment configurer les webhooks ?

**R:**
1. Allez dans **Administration > Webhooks**
2. Créez un nouveau webhook avec votre URL
3. Sélectionnez les événements à surveiller
4. Configurez le secret pour la sécurité

## Maintenance et Dépannage

### Q: Comment sauvegarder les données de paie ?

**R:**
- Sauvegarde automatique quotidienne de la base de données
- Export manuel des données importantes
- Sauvegarde des fichiers PDF générés
- Voir le [Guide de Sauvegarde](../administration/backup-restore.md)

### Q: Que faire en cas de panne système ?

**R:**
1. Vérifiez l'état des services (base de données, Redis, Celery)
2. Consultez les logs d'erreur
3. Redémarrez les services si nécessaire
4. Contactez le support technique si le problème persiste

### Q: Comment mettre à jour le système ?

**R:**
1. Sauvegardez les données
2. Arrêtez les services
3. Mettez à jour le code
4. Exécutez les migrations de base de données
5. Redémarrez les services
6. Vérifiez le bon fonctionnement

## Erreurs Courantes

### Q: "Aucun employé traité" lors du traitement

**R:** Vérifiez :
- Les contrats sont actifs pour la période
- Les dates de contrat sont correctes
- Les employés ne sont pas suspendus
- Les paramètres de filtrage

### Q: "Token invalide ou expiré"

**R:**
- Reconnectez-vous pour obtenir un nouveau token
- Vérifiez la configuration JWT
- Assurez-vous que l'horloge système est correcte

### Q: "Erreur de calcul salarial"

**R:**
- Vérifiez les données contractuelles
- Contrôlez les paramètres de paie
- Consultez les logs détaillés
- Testez avec un employé individuel

### Q: "Dépassement de plafond INSS"

**R:**
- Vérifiez les plafonds configurés (27,000 pour pension, 2,400 pour risque)
- Assurez-vous que les calculs respectent les plafonds
- Contrôlez les paramètres de cotisation

## Support et Assistance

### Q: Comment obtenir de l'aide ?

**R:**
1. Consultez cette documentation
2. Vérifiez les [guides utilisateur](../user-guides/)
3. Consultez les [guides de dépannage](../administration/troubleshooting.md)
4. Contactez le support technique

### Q: Comment signaler un bug ?

**R:**
1. Reproduisez le problème
2. Collectez les informations (logs, captures d'écran)
3. Décrivez les étapes pour reproduire
4. Contactez l'équipe de développement

### Q: Comment demander une nouvelle fonctionnalité ?

**R:**
1. Décrivez le besoin métier
2. Proposez une solution
3. Évaluez l'impact sur les processus existants
4. Soumettez la demande à l'équipe produit

---

## Ressources Utiles

- [Guide de Démarrage Rapide](../user-guides/quick-start.md)
- [Configuration Système](../configuration/system-setup.md)
- [Référence API](api-reference.md)
- [Dépannage](../administration/troubleshooting.md)
- [Glossaire](glossary.md)

---

*Cette FAQ est mise à jour régulièrement. Si votre question n'y figure pas, n'hésitez pas à contacter le support.*
