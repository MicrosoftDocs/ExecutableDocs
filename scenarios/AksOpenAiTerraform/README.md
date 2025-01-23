---
title: How to deploy and run an Azure OpenAI ChatGPT application on AKS via Terraform
description: This article shows how to deploy an AKS cluster and Azure OpenAI Service via Terraform and how to deploy a ChatGPT-like application in Python.
ms.topic: quickstart 
ms.date: 09/06/2024 
author: aamini7 
ms.author: ariaamini
ms.custom: innovation-engine, linux-related-content 
---

## Install AKS extension

Run commands below to set up AKS extensions for Azure.

```bash
./scripts/register-preview-features.sh
```

## Set up Subscription ID to authenticate for Terraform

Terraform uses the ARM_SUBSCRIPTION_ID environment variable to authenticate while using CLI.

```bash
export ARM_SUBSCRIPTION_ID="0c8875c7-e423-4caa-827a-1f0350bd8dd3"
```

## Init Terraform

```bash
terraform init
```

## Run Terraform

```bash
terraform apply
```
