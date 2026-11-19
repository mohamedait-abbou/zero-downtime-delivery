# Post 1 — Lancement (français)

**À publier :** après la semaine 3, quand le canary et le rollback fonctionnent.
**Images :** la page de statut + le graphe Grafana.
**À remplir :** chaque `[X]` avec un vrai chiffre, sinon supprime la ligne.

---

J'ai déployé une version cassée exprès.

Elle n'a jamais atteint 100 % du trafic.

Voici ce qui s'est passé :

J'ai poussé une image dont l'endpoint `/ready` échouait après 10 secondes.
Le canary a reçu 10 % du trafic.
Prometheus a détecté la hausse du taux d'erreur.
Le déploiement a été annulé.
Le trafic est revenu à l'ancienne version.

L'ancienne version n'a jamais arrêté de répondre.

C'est toute la différence entre « ça marche sur ma machine » et « ça marche en
production ».

J'ai donc construit une petite plateforme de livraison pour apprendre cette
différence :

→ GitHub Actions : tests, build, scan, signature
→ GHCR : chaque image est taguée avec le SHA du commit
→ ArgoCD : le déploiement part de Git, pas de mon terminal
→ Kubernetes : les probes décident quand un pod reçoit du trafic
→ Prometheus + Grafana : le canary est jugé sur des données, pas sur l'espoir
→ Terraform : les réglages du dépôt sont aussi du code

Coût : 0 €.
Cluster kind local, registry gratuit, CI gratuite.

Trois choses que je n'avais pas comprises avant de le construire :

1. Un déploiement n'est pas fini quand il démarre. Il est fini quand l'analyse
   passe.

2. « Healthy » et « ready » sont deux questions différentes. La liveness
   redémarre le processus. La readiness le retire du trafic. Les confondre
   aggrave la panne.

3. Si on ne sait pas mesurer l'échec, on ne peut pas automatiser le rollback.
   La règle doit exister avant le déploiement.

Le dépôt, l'architecture et les limites sont ici :
[lien]

#DevOps #Kubernetes #CICD #SRE #Maroc

---

## Notes

- Garde les deux premières lignes telles quelles : c'est le hook.
- Les trois leçons sont la partie que les gens enregistrent.
- Ajoute une phrase honnête : « Le cluster est mono-nœud et local, ce n'est pas
  de la haute disponibilité, et c'est écrit dans le README. »
- En français, les recruteurs marocains lisent surtout le début. Ne mets pas de
  preamble.
