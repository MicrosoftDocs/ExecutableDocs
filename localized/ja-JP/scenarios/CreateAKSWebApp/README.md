---
title: Azure CLI を使用して拡張性があり、安全な Azure Kubernetes Service クラスターをデプロイする
description: このチュートリアルでは、HTTP を介してセキュリティで保護された Azure Kubernetes Web アプリケーションを作成する手順を説明します。
author: mbifeld
ms.author: mbifeld
ms.topic: article
ms.date: 11/28/2023
ms.custom: innovation-engine
---

# クイック　スタート: Azure CLI を使用して、拡張性があり安全な Azure Kubernetes Service クラスターをデプロイする

[![Azure に配置する](https://aka.ms/deploytoazurebutton)](https://go.microsoft.com/fwlink/?linkid=2286416)

https を介してセキュリティで保護された Azure Kubernetes Web アプリケーションを作成する手順を説明するこのチュートリアルをご覧ください。 このチュートリアルは、既に Azure CLI にログインしており、CLI で使用するサブスクリプションが選択されていることを前提としています。 また、Helm がインストールされていることを前提としています ([手順はこちら](https://helm.sh/docs/intro/install/))。

## 環境変数を定義する

このチュートリアルの最初の手順は、環境変数を定義することです。

```bash
export RANDOM_ID="$(openssl rand -hex 3)"
export NETWORK_PREFIX="$(($RANDOM % 254 + 1))"
export SSL_EMAIL_ADDRESS="$(az account show --query user.name --output tsv)"
export MY_RESOURCE_GROUP_NAME="myAKSResourceGroup$RANDOM_ID"
export REGION="westeurope"
export MY_AKS_CLUSTER_NAME="myAKSCluster$RANDOM_ID"
export MY_PUBLIC_IP_NAME="myPublicIP$RANDOM_ID"
export MY_DNS_LABEL="mydnslabel$RANDOM_ID"
export MY_VNET_NAME="myVNet$RANDOM_ID"
export MY_VNET_PREFIX="10.$NETWORK_PREFIX.0.0/16"
export MY_SN_NAME="mySN$RANDOM_ID"
export MY_SN_PREFIX="10.$NETWORK_PREFIX.0.0/22"
export FQDN="${MY_DNS_LABEL}.${REGION}.cloudapp.azure.com"
```

## リソース グループの作成

リソース グループとは、関連リソース用のコンテナーです。 すべてのリソースをリソース グループに配置する必要があります。 このチュートリアルに必要なものを作成します。 次のコマンドは、事前定義済みの $MY_RESOURCE_GROUP_NAME パラメーターと $REGION パラメーターを使用してリソース グループを作成します。

```bash
az group create --name $MY_RESOURCE_GROUP_NAME --location $REGION
```

結果:

<!-- expected_similarity=0.3 -->

```JSON
{
  "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myAKSResourceGroupxxxxxx",
  "location": "eastus",
  "managedBy": null,
  "name": "testResourceGroup",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": null,
  "type": "Microsoft.Resources/resourceGroups"
}
```

## 仮想ネットワークとサブネットの作成

仮想ネットワークは、Azure 内のプライベート ネットワークの基本的な構成ブロックです。 Azure Virtual Network では、VM などの Azure リソースが、相互に、およびインターネットと安全に通信することができます。

```bash
az network vnet create \
    --resource-group $MY_RESOURCE_GROUP_NAME \
    --location $REGION \
    --name $MY_VNET_NAME \
    --address-prefix $MY_VNET_PREFIX \
    --subnet-name $MY_SN_NAME \
    --subnet-prefixes $MY_SN_PREFIX
```

結果:

<!-- expected_similarity=0.3 -->

```JSON
{
  "newVNet": {
    "addressSpace": {
      "addressPrefixes": [
        "10.xxx.0.0/16"
      ]
    },
    "enableDdosProtection": false,
    "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/myAKSResourceGroupxxxxxx/providers/Microsoft.Network/virtualNetworks/myVNetxxx",
    "location": "eastus",
    "name": "myVNetxxx",
    "provisioningState": "Succeeded",
    "resourceGroup": "myAKSResourceGroupxxxxxx",
    "subnets": [
      {
        "addressPrefix": "10.xxx.0.0/22",
        "delegations": [],
        "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/myAKSResourceGroupxxxxxx/providers/Microsoft.Network/virtualNetworks/myVNetxxx/subnets/mySNxxx",
        "name": "mySNxxx",
        "privateEndpointNetworkPolicies": "Disabled",
        "privateLinkServiceNetworkPolicies": "Enabled",
        "provisioningState": "Succeeded",
        "resourceGroup": "myAKSResourceGroupxxxxxx",
        "type": "Microsoft.Network/virtualNetworks/subnets"
      }
    ],
    "type": "Microsoft.Network/virtualNetworks",
    "virtualNetworkPeerings": []
  }
}
```

## AKS Azure リソース プロバイダーを登録する

Microsoft.OperationsManagement と Microsoft.OperationalInsights プロバイダーがサブスクリプションで登録されていることを確認してください。 これらは、[Container Insights](https://docs.microsoft.com/azure/azure-monitor/containers/container-insights-overview) をサポートするために必要な Azure リソース プロバイダーです。 登録の状態を確認するには、次のコマンドを実行します

```bash
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.OperationsManagement
az provider register --namespace Microsoft.OperationalInsights
```

## AKS クラスターを作成

az aks create コマンドを、Container insights を有効にする --enable-addons monitoring パラメーターと共に使用して、AKS クラスターを作成します。 次の例では、自動スケーリング、可用性ゾーン対応クラスターを作成します。

この処理には数分かかります。

```bash
export MY_SN_ID=$(az network vnet subnet list --resource-group $MY_RESOURCE_GROUP_NAME --vnet-name $MY_VNET_NAME --query "[0].id" --output tsv)
az aks create \
  --resource-group $MY_RESOURCE_GROUP_NAME \
  --name $MY_AKS_CLUSTER_NAME \
  --auto-upgrade-channel stable \
  --enable-cluster-autoscaler \
  --enable-addons monitoring \
  --location $REGION \
  --node-count 1 \
  --min-count 1 \
  --max-count 3 \
  --network-plugin azure \
  --network-policy azure \
  --vnet-subnet-id $MY_SN_ID \
  --no-ssh-key \
  --node-vm-size Standard_DS2_v2 \
  --zones 1 2 3
```

## クラスターに接続する

Kubernetes クラスターを管理するには、Kubernetes のコマンドライン クライアントである kubectl を使います。 Azure Cloud Shell を使用している場合、kubectl は既にインストールされています。

1. az aks install-cli コマンドを使用して az aks CLI をローカルにインストールする

   ```bash
   if ! [ -x "$(command -v kubectl)" ]; then az aks install-cli; fi
   ```

2. az aks get-credentials コマンドを使用して、Kubernetes クラスターに接続するように kubectl を構成します。 次のコマンドで、以下を行います。

   - 資格情報をダウンロードし、それを使用するように Kubernetes CLI を構成します。
   - ~/.kube/config (Kubernetes 構成ファイルの既定の場所) を使用します。 Kubernetes 構成ファイルに対して別の場所を指定するには、--file 引数を使用します。

   > [!WARNING]
   > これにより、同じエントリを使用して既存の資格情報が上書きされます

   ```bash
   az aks get-credentials --resource-group $MY_RESOURCE_GROUP_NAME --name $MY_AKS_CLUSTER_NAME --overwrite-existing
   ```

3. kubectl get コマンドを使用して、ご利用のクラスターへの接続を確認します。 このコマンドでは、クラスター ノードの一覧が返されます。

   ```bash
   kubectl get nodes
   ```

## NGINX イングレス コントローラーをインストールする

```bash
export MY_STATIC_IP=$(az network public-ip create --resource-group MC_${MY_RESOURCE_GROUP_NAME}_${MY_AKS_CLUSTER_NAME}_${REGION} --location ${REGION} --name ${MY_PUBLIC_IP_NAME} --dns-name ${MY_DNS_LABEL} --sku Standard --allocation-method static --version IPv4 --zone 1 2 3 --query publicIp.ipAddress -o tsv)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-dns-label-name"=$MY_DNS_LABEL \
  --set controller.service.loadBalancerIP=$MY_STATIC_IP \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --wait
```

## アプリケーションのデプロイ

Kubernetes のマニフェスト ファイルでは、どのコンテナー イメージを実行するかなど、クラスターの望ましい状態を定義します。

このクイックスタートでは、マニフェストを使用して、Azure Vote アプリケーションを実行するために必要なすべてのオブジェクトを作成します。 このマニフェストには、次の 2 つの Kubernetes デプロイが含まれています。

- サンプルの Azure Vote Python アプリケーション。
- Redis インスタンス。

次の 2 つの Kubernetes サービスも作成されます。

- Redis インスタンス用の内部サービス。
- インターネットから Azure Vote アプリケーションにアクセスするための外部サービス。

最後に、トラフィックを Azure Vote アプリケーションにルーティングするためのイングレス リソースが作成されます。

テスト投票アプリの YML ファイルは既に準備されています。 

```bash
cat << EOF > azure-vote-start.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
      containers:
      - name: rabbitmq
        image: mcr.microsoft.com/mirror/docker/library/rabbitmq:3.10-management-alpine
        ports:
        - containerPort: 5672
          name: rabbitmq-amqp
        - containerPort: 15672
          name: rabbitmq-http
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: "username"
        - name: RABBITMQ_DEFAULT_PASS
          value: "password"
        resources:
          requests:
            cpu: 10m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
        volumeMounts:
        - name: rabbitmq-enabled-plugins
          mountPath: /etc/rabbitmq/enabled_plugins
          subPath: enabled_plugins
      volumes:
      - name: rabbitmq-enabled-plugins
        configMap:
          name: rabbitmq-enabled-plugins
          items:
          - key: rabbitmq_enabled_plugins
            path: enabled_plugins
---
apiVersion: v1
data:
  rabbitmq_enabled_plugins: |
    [rabbitmq_management,rabbitmq_prometheus,rabbitmq_amqp1_0].
kind: ConfigMap
metadata:
  name: rabbitmq-enabled-plugins
---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
spec:
  selector:
    app: rabbitmq
  ports:
    - name: rabbitmq-amqp
      port: 5672
      targetPort: 5672
    - name: rabbitmq-http
      port: 15672
      targetPort: 15672
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
      containers:
      - name: order-service
        image: ghcr.io/azure-samples/aks-store-demo/order-service:latest
        ports:
        - containerPort: 3000
        env:
        - name: ORDER_QUEUE_HOSTNAME
          value: "rabbitmq"
        - name: ORDER_QUEUE_PORT
          value: "5672"
        - name: ORDER_QUEUE_USERNAME
          value: "username"
        - name: ORDER_QUEUE_PASSWORD
          value: "password"
        - name: ORDER_QUEUE_NAME
          value: "orders"
        - name: FASTIFY_ADDRESS
          value: "0.0.0.0"
        resources:
          requests:
            cpu: 1m
            memory: 50Mi
          limits:
            cpu: 75m
            memory: 128Mi
      initContainers:
      - name: wait-for-rabbitmq
        image: busybox
        command: ['sh', '-c', 'until nc -zv rabbitmq 5672; do echo waiting for rabbitmq; sleep 2; done;']
        resources:
          requests:
            cpu: 1m
            memory: 50Mi
          limits:
            cpu: 75m
            memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 3000
    targetPort: 3000
  selector:
    app: order-service
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
      containers:
      - name: product-service
        image: ghcr.io/azure-samples/aks-store-demo/product-service:latest
        ports:
        - containerPort: 3002
        resources:
          requests:
            cpu: 1m
            memory: 1Mi
          limits:
            cpu: 1m
            memory: 7Mi
---
apiVersion: v1
kind: Service
metadata:
  name: product-service
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 3002
    targetPort: 3002
  selector:
    app: product-service
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: store-front
spec:
  replicas: 1
  selector:
    matchLabels:
      app: store-front
  template:
    metadata:
      labels:
        app: store-front
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
      containers:
      - name: store-front
        image: ghcr.io/azure-samples/aks-store-demo/store-front:latest
        ports:
        - containerPort: 8080
          name: store-front
        env:
        - name: VUE_APP_ORDER_SERVICE_URL
          value: "http://order-service:3000/"
        - name: VUE_APP_PRODUCT_SERVICE_URL
          value: "http://product-service:3002/"
        resources:
          requests:
            cpu: 1m
            memory: 200Mi
          limits:
            cpu: 1000m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: store-front
spec:
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: store-front
  type: LoadBalancer
EOF
```

このアプリをデプロイするには、次のコマンドを実行します。

```bash
kubectl apply -f azure-vote-start.yml
```

## アプリケーションをテストする

パブリック IP またはアプリケーションの URL のいずれかにアクセスして、アプリケーションが実行されていることを確認します。 次のコマンドを実行して、アプリケーション URL を検索できます。

> [!Note]
> POD が作成され、HTTP 経由でサイトにアクセスできるようになるまで、2 ~ 3 分かかる場合が多くあります。

```bash
runtime="5 minute";
endtime=$(date -ud "$runtime" +%s);
while [[ $(date -u +%s) -le $endtime ]]; do
   STATUS=$(kubectl get pods -l app=azure-vote-front -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}'); echo $STATUS;
   if [ "$STATUS" == 'True' ]; then
      break;
   else
      sleep 10;
   fi;
done
```

```bash
curl "http://$FQDN"
```

結果:

<!-- expected_similarity=0.3 -->

```HTML
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <link rel="stylesheet" type="text/css" href="/static/default.css">
    <title>Azure Voting App</title>

    <script language="JavaScript">
        function send(form){
        }
    </script>

</head>
<body>
    <div id="container">
        <form id="form" name="form" action="/"" method="post"><center>
        <div id="logo">Azure Voting App</div>
        <div id="space"></div>
        <div id="form">
        <button name="vote" value="Cats" onclick="send()" class="button button1">Cats</button>
        <button name="vote" value="Dogs" onclick="send()" class="button button2">Dogs</button>
        <button name="vote" value="reset" onclick="send()" class="button button3">Reset</button>
        <div id="space"></div>
        <div id="space"></div>
        <div id="results"> Cats - 0 | Dogs - 0 </div>
        </form>
        </div>
    </div>
</body>
</html>
```

## カスタム ドメインへの HTTPS 終了の追加

チュートリアルのこの時点で、NGINX をイングレス コントローラーとして使用した AKS Web アプリと、アプリケーションへのアクセスに使用できるカスタム ドメインがあります。 次の手順は、ユーザーが HTTPS 経由で安全にアプリケーションにアクセスできるように、ドメインに SSL 証明書を追加することです。

## Cert Manager を設定する

HTTPS を追加するには、Cert Manager を使用します。 Cert Manager は、Kubernetes デプロイ用の SSL 証明書の取得と管理に使用されるオープン ソース ツールです。 Cert Manager は、一般的なパブリック発行元やプライベート発行元など、さまざまな発行元から証明書を取得し、証明書が有効で最新であることを保証します。これにより、証明書の期限が切れる前に構成時点への更新が試行されます。

1. cert-manager をインストールするには、最初にそれを実行する名前空間を作成する必要があります。 このチュートリアルでは、cert-manager を cert-manager 名前空間にインストールします。 配置マニフェストに変更を加える必要がありますが、別の名前空間で cert-manager を実行できます。

   ```bash
   kubectl create namespace cert-manager
   ```

2. これで、cert-manager をインストールできるようになりました。 すべてのリソースは、1 つの YAML マニフェスト ファイルに含まれます。 これは、次のコマンドを実行してインストールできます。

   ```bash
   kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.0/cert-manager.crds.yaml
   ```

3. 次のコマンドを実行して、certmanager.k8s.io/disable-validation: "true "ラベルを cert-manager 名前空間に追加します。 これにより、cert-manager が TLS をブートストラップするために必要なシステム リソースを独自の名前空間に作成できるようになります。

   ```bash
   kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
   ```

## Helm Charts を介して証明書を取得する

Helm は、Kubernetes クラスターへのアプリケーションやサービスの作成、パッケージ化、構成、デプロイを自動化するための Kubernetes デプロイ ツールです。

cert-manager では、Kubernetes への第一級のインストール方法として Helm チャートが提供されます。

1. Jetstack Helm リポジトリを追加する

   このリポジトリは、cert-manager チャートの唯一のサポート ソースです。 インターネット上には他にもいくつかのミラーやコピーがありますが、それらはすべて非公式なものであり、セキュリティ上のリスクがあります。

   ```bash
   helm repo add jetstack https://charts.jetstack.io
   ```

2. ローカルの Helm Chart リポジトリ キャッシュを更新する

   ```bash
   helm repo update
   ```

3. 次のコマンドを実行して、helm を介して dert-manager アドオンをインストールします。

   ```bash
   helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.7.0
   ```

4. 証明書の発行者 YAML ファイルを適用する

   ClusterIssuers は、証明書署名要求を許可することで署名付き証明書を生成できる証明機関 (CA) を表す Kubernetes リソースです。 すべての cert-manager 証明書は、要求の許可を試行する準備の整った参照発行者が必要です。
   使用する発行者は `cluster-issuer-prod.yml file` で確認できます
        
    ```bash
    cat <<EOF > cluster-issuer-prod.yml
    apiVersion: cert-manager.io/v1
    kind: ClusterIssuer
    metadata:
      name: letsencrypt-prod
    spec:
      acme:
        # You must replace this email address with your own.
        # Let's Encrypt will use this to contact you about expiring
        # certificates, and issues related to your account.
        email: $SSL_EMAIL_ADDRESS
        # ACME server URL for Let’s Encrypt’s prod environment.
        # The staging environment will not issue trusted certificates but is
        # used to ensure that the verification process is working properly
        # before moving to production
        server: https://acme-v02.api.letsencrypt.org/directory
        # Secret resource used to store the account's private key.
        privateKeySecretRef:
          name: letsencrypt
        # Enable the HTTP-01 challenge provider
        # you prove ownership of a domain by ensuring that a particular
        # file is present at the domain
        solvers:
        - http01:
            ingress:
              class: nginx
            podTemplate:
              spec:
                nodeSelector:
                  "kubernetes.io/os": linux
    EOF
    ```

    ```bash
    cluster_issuer_variables=$(<cluster-issuer-prod.yml)
    ```

5. Voting App アプリケーションを更新し、cert-manager を使用して SSL 証明書を取得します。

   完全な YAML ファイルは `azure-vote-nginx-ssl.yml` にあります。

```bash
cat << EOF > azure-vote-nginx-ssl.yml
---
# INGRESS WITH SSL PROD
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vote-ingress
  namespace: default
  annotations:
    kubernetes.io/tls-acme: "true"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - $FQDN
    secretName: azure-vote-nginx-secret
  rules:
    - host: $FQDN
      http:
        paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: azure-vote-front
              port:
                number: 80
EOF
```

    ```bash
    azure_vote_nginx_ssl_variables=$(<azure-vote-nginx-ssl.yml)
    echo "${azure_vote_nginx_ssl_variables//\$FQDN/$FQDN}" | kubectl apply -f -
    ```

<!--## Validate application is working

Wait for the SSL certificate to issue. The following command will query the 
status of the SSL certificate for 3 minutes. In rare occasions it may take up to 
15 minutes for Lets Encrypt to issue a successful challenge and 
the ready state to be 'True'

```bash
runtime="10 minute"; endtime=$(date -ud "$runtime" +%s); while [[ $(date -u +%s) -le $endtime ]]; do STATUS=$(kubectl get certificate --output jsonpath={..status.conditions[0].status}); echo $STATUS; if [ "$STATUS" = 'True' ]; then break; else sleep 10; fi; done
```

Validate SSL certificate is True by running the follow command:

```bash
kubectl get certificate --output jsonpath={..status.conditions[0].status}
```

Results:

<!-- expected_similarity=0.3 -->
<!--
```ASCII
True
```
-->

## HTTPS を介してセキュリティで保護された AKS デプロイの閲覧

次のコマンドを実行して、アプリケーションの HTTPS エンドポイントを取得します。

> [!Note]
> SSL 証明書が反映され、HTTP 経由でサイトにアクセスできるようになるまで、2 ~ 3 分かかる場合が多くあります。

```bash
runtime="5 minute";
endtime=$(date -ud "$runtime" +%s);
while [[ $(date -u +%s) -le $endtime ]]; do
   STATUS=$(kubectl get svc --namespace=ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}');
   echo $STATUS;
   if [ "$STATUS" == "$MY_STATIC_IP" ]; then
      break;
   else
      sleep 10;
   fi;
done
```

```bash
echo "You can now visit your web server at https://$FQDN"
```

## 次のステップ

- [Azure Kubernetes Service ドキュメント](https://learn.microsoft.com/azure/aks/)
- [Azure Container Registry を作成する](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-prepare-acr?tabs=azure-cli)
- [AKS でアプリケーションをスケーリングする](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-scale?tabs=azure-cli)
- [AKS でアプリケーションを更新する](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-app-update?tabs=azure-cli)