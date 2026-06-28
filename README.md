# devsecops-training-demo

Projet d'entraînement minimaliste pour comprendre et pratiquer un modèle de
branching / CI / CD / promotion d'artefacts **indépendant de tout outil**
(le même principe fonctionne avec GitHub, Gitea, GitLab...).

## Le modèle en une phrase

> **2 branches permanentes** (`develop`, `main`) génèrent **3 niveaux de
> maturité d'artefacts** (Scratch, Staging, Stable), et **CI ≠ CD** :
> la CI valide, le CD publie, et la promotion ne reconstruit jamais rien.

```
main        ●────────────────●─────────────────●──    (≈ prod / "Stable")
             \                \                 \
develop       ●──●──●──●──●────●──●──●──●──●──●──●──   (≈ staging)
                  \        \  /  /
feature/xxx        ●───●───●     (jetable, supprimée après merge → "Scratch")
```

| Branche | Permanente ? | Déclenche |
|---|---|---|
| `main` | ✅ | rien directement — reçoit des promotions manuelles |
| `develop` | ✅ | CI à chaque push ; CD-staging à chaque tag `vX.Y.Z` |
| `feature/*`, `fix/*` | ❌ (éphémère) | CI uniquement |

## CI vs CD : pourquoi deux fichiers séparés

| | CI (`ci.yml`) | CD (`cd-staging.yml`, `cd-promote.yml`) |
|---|---|---|
| Question posée | "Le code est-il correct ?" | "Je publie un artefact" |
| Déclencheur | push sur `feature/*`/`fix/*`/`develop`, et toute Pull Request | tag `vX.Y.Z` (staging) / déclenchement manuel (promote) |
| Publie-t-il quelque chose ? | **Non, jamais** | **Oui, c'est son seul but** |
| Permissions nécessaires | lecture seule | écriture sur le registre (`packages: write`) |

Cette séparation est volontaire et c'est une bonne pratique : un pipeline qui
ne fait que valider n'a besoin d'aucun droit d'écriture sur le registre — on
réduit la surface d'attaque (principe du moindre privilège).

## Les 3 niveaux de maturité d'artefact

| Niveau | Déclencheur | Tag de l'image | Build ? |
|---|---|---|---|
| **Scratch** | push sur `feature/*` (ici limité à la CI, pas de publication — à toi de l'étendre si tu veux publier du jetable) | — | CI uniquement dans cette démo |
| **Staging** | `git tag v1.0.0` sur `develop` | `staging-1.0.0` | ✅ Build + push (le SEUL build) |
| **Stable** | déclenchement manuel `cd-promote.yml` après merge `develop → main` | `stable-1.0.0` | ❌ Aucun rebuild — copie de manifeste |

## Mode d'emploi pas-à-pas pour t'entraîner

### 0. Préparer le repo sur GitHub

```bash
cd devsecops-training-demo
git init
git add .
git commit -m "Initial commit: app + CI/CD workflows"
git branch -M main
git remote add origin https://github.com/<ton-compte>/devsecops-training-demo.git
git push -u origin main

# Créer develop à partir de main
git checkout -b develop
git push -u origin develop
```

### 1. Protéger les branches (sur GitHub : Settings → Branches)

- **`main`** :
  - "Require a pull request before merging" ✅
  - "Require approvals" = 1 minimum
  - "Do not allow bypassing the above settings" ✅
  - (optionnel) restreindre qui peut merger à une équipe "ops" si tu as une org GitHub
- **`develop`** :
  - "Require a pull request before merging" ✅ (au minimum pour les feature/*)

### 2. Protéger l'environnement de promotion (Settings → Environments → `production`)

- Crée un environnement nommé `production`
- Ajoute un "Required reviewer" (toi-même, ou un compte "ops" si tu en as un second)
- Résultat : `cd-promote.yml` ne s'exécutera qu'après validation manuelle dans l'onglet Actions

### 3. Simuler un cycle de développement complet

```bash
# --- Niveau Scratch : travail de dev ---
git checkout develop
git checkout -b feature/health-message
# modifie app/main.py, par exemple change le message de /health
git add . && git commit -m "feat: improve health message"
git push -u origin feature/health-message
# -> Ouvre une Pull Request feature/health-message -> develop sur GitHub
# -> Observe : ci.yml se déclenche, AUCUNE publication

# Merge la PR (depuis l'interface GitHub), puis :
git checkout develop
git pull

# --- Niveau Staging : on fige une version ---
git tag v1.0.0
git push origin v1.0.0
# -> Observe : cd-staging.yml se déclenche
# -> Une image ghcr.io/<toi>/devsecops-training-demo:staging-1.0.0 est publiée
# -> Visible dans l'onglet "Packages" de ton profil GitHub

# --- Niveau Stable : promotion vers la prod ---
# Ouvre une Pull Request develop -> main, fais-la approuver, merge.
git checkout main
git pull

# Va dans l'onglet "Actions" -> "CD - Promote Staging to Stable" -> "Run workflow"
# Renseigne version = 1.0.0
# -> Le job attend la validation de l'environnement "production" (reviewer)
# -> Une fois approuvé : copie staging-1.0.0 -> stable-1.0.0, SANS rebuild
# -> Le job vérifie que les deux digests SHA256 sont identiques
```

### 4. Vérifier par toi-même qu'il n'y a pas eu de rebuild

```bash
docker buildx imagetools inspect ghcr.io/<toi>/devsecops-training-demo:staging-1.0.0
docker buildx imagetools inspect ghcr.io/<toi>/devsecops-training-demo:stable-1.0.0
# Compare le champ "Digest" : il doit être RIGOUREUSEMENT identique.
```

## Pour aller plus loin (une fois ce modèle bien assimilé)

- Ajouter un job de scan (Trivy, Gitleaks, Semgrep) dans `ci.yml`
- Publier aussi le niveau "Scratch" (image éphémère, purge automatique après N jours)
- Remplacer `workflow_dispatch` manuel par un déclenchement automatique sur
  push vers `main`, en lisant la version depuis un fichier `VERSION` versionné
- Générer un SBOM (Syft) et signer l'image (Cosign) au moment du build staging
  — jamais au moment de la promotion, puisque l'image ne change pas
