---
title: "Vue d’ensemble du déploiement d’une base de données PostgreSQL hautement disponible sur AKS avec Azure\_CLI"
description: Découvrez comment déployer une base de données PostgreSQL hautement disponible sur AKS en utilisant l’opérateur CloudNativePG.
ms.topic: overview
ms.date: 06/07/2024
author: kenkilty
ms.author: kkilty
ms.custom: 'innovation-engine, aks-related-content'
---
# Déployer une base de données PostgreSQL hautement disponible sur AKS avec Azure CLI

Dans ce guide, vous allez déployer un cluster PostgreSQL hautement disponible qui couvre plusieurs zones de disponibilité Azure sur AKS avec Azure CLI.

Cet article s’attarde sur les prérequis applicables à la configuration d’un cluster PostgreSQL sur [Azure Kubernetes Service (AKS)][what-is-aks] et offre une vue d’ensemble du processus de déploiement complet et de l’architecture.

[!INCLUDE [open source disclaimer](./includes/open-source-disclaimer.md)]

## Prérequis

* Ce guide suppose une compréhension de base des [concepts clés de Kubernetes][core-kubernetes-concepts] et de [PostgreSQL][postgresql].
* Vous avez besoin des [rôles intégrés][azure-roles] **Propriétaire** ou **Administrateur d’accès utilisateur** et **Contributeur** dans un abonnement de votre compte Azure.

[!INCLUDE [azure-cli-prepare-your-environment-no-header.md](~/reusable-content/azure-cli/azure-cli-prepare-your-environment-no-header.md)]

* Vous devez également avoir installé les ressources suivantes :

  * [Azure CLI](/cli/azure/install-azure-cli), version 2.56 ou ultérieure.
  * [Extension de préversion d’Azure Kubernetes Service (AKS)][aks-preview].
  * [jq][jq] version 1.5 ou ultérieure.
  * [kubectl][install-kubectl] version 1.21.0 ou ultérieure.
  * [Helm][install-helm] version 3.0.0 ou ultérieure.
  * [openssl][install-openssl] version 3.3.0 ou ultérieure.
  * [Visual Studio Code][install-vscode] ou équivalent.
  * [Krew][install-krew] version 0.4.4 ou ultérieure.
  * [Plug-in kubectl CloudNativePG (CNPG)][cnpg-plugin].

## Processus de déploiement

Dans ce guide, vous apprendrez comment :

* Utiliser Azure CLI pour créer un cluster AKS multizone.
* Déployer un cluster et une base de données PostgreSQL hautement disponibles en utilisant l’[opérateur CNPG][cnpg-plugin].
* Configurer le monitoring pour PostgreSQL à l’aide de Prometheus et de Grafana.
* Déployer un exemple de jeu de données sur une base de données PostgreSQL.
* Effectuer des mises à niveau de cluster PostgreSQL et AKS.
* Simuler une interruption de cluster et un basculement de réplica PostgreSQL.
* Effectuer la sauvegarde et la restauration d’une base de données PostgreSQL.

## Architecture de déploiement

Ce diagramme illustre une configuration de cluster PostgreSQL avec un réplica principal et deux réplicas en lecture managés par l’opérateur [CloudNativePG (CNPG)](https://cloudnative-pg.io/). L’architecture fournit une base de données PostgreSQL hautement disponible s’exécutant sur un cluster AKS capable de résister à une panne de zone en assurant une basculement entre réplicas.

Les sauvegardes sont stockées sur [Stockage Blob Azure](/azure/storage/blobs/), ce qui offre un autre moyen de restaurer la base de données en cas de problème de réplication de streaming à partir du réplica principal.

:::image source="./media/postgresql-ha-overview/architecture-diagram.png" alt-text="Diagramme de l’architecture CNPG." lightbox="./media/postgresql-ha-overview/architecture-diagram.png":::

> [!NOTE]
> Pour les applications qui nécessitent une séparation des données au niveau de la base de données, vous pouvez ajouter d’autres bases de données avec des commandes postInitSQL et d’autres commandes similaires. Il n’est actuellement pas possible d’ajouter d’autres bases de données de manière déclarative avec l’opérateur CNPG.
[Découvrez-en plus](https://github.com/cloudnative-pg/cloudnative-pg) sur l’opérateur CNPG. 

## Étapes suivantes

> [!div class="nextstepaction"]
> [Créer l’infrastructure en vue du déploiement d’une base de données PostgreSQL hautement disponible sur AKS en utilisant l’opérateur CloudNativePG][create-infrastructure]

## Contributeurs

*Cet article est géré par Microsoft. Il a été écrit à l’origine par les contributeurs* suivants :

* Ken Kitty | Responsable de programme technique principal
* Russell de Pina | Responsable de programme technique principal
* Adrian Joian | Ingénieur client senior
* Jenny Hayes | Développeuse de contenu confirmée
* Carol Smith | Développeuse de contenu confirmée
* Erin Schaffer | Développeuse de contenu 2
* Adam Sharif | Ingénieur client 2

<!-- LINKS -->
[what-is-aks]: ./what-is-aks.md
[postgresql]: https://www.postgresql.org/
[core-kubernetes-concepts]: ./concepts-clusters-workloads.md
[azure-roles]: /azure/role-based-access-control/built-in-roles
[aks-preview]: ./draft.md#install-the-aks-preview-azure-cli-extension
[jq]: https://jqlang.github.io/jq/
[install-kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[install-helm]: https://helm.sh/docs/intro/install/
[install-openssl]: https://www.openssl.org/
[install-vscode]: https://code.visualstudio.com/Download
[install-krew]: https://krew.sigs.k8s.io/
[cnpg-plugin]: https://cloudnative-pg.io/documentation/current/kubectl-plugin/#using-krew
[create-infrastructure]: ./create-postgresql-ha.md
