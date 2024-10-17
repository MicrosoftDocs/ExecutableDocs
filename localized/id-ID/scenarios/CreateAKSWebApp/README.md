---
title: Menyebarkan kluster Azure Kubernetes Service yang Dapat Diskalakan & Aman menggunakan Azure CLI
description: Tutorial ini di mana kami akan membawa Anda selangkah demi selangkah dalam membuat Aplikasi Web Azure Kubernetes yang diamankan melalui https.
author: mbifeld
ms.author: mbifeld
ms.topic: article
ms.date: 11/28/2023
ms.custom: innovation-engine
---

# Mulai Cepat: Menyebarkan kluster Azure Kubernetes Service yang Dapat Diskalakan & Aman menggunakan Azure CLI

[![Sebarkan ke Azure](https://aka.ms/deploytoazurebutton)](https://go.microsoft.com/fwlink/?linkid=2286416)

Selamat datang di tutorial ini di mana kami akan membawa Anda langkah demi langkah dalam membuat Aplikasi Web Azure Kubernetes yang diamankan melalui https. Tutorial ini mengasumsikan Anda sudah masuk ke Azure CLI dan telah memilih langganan untuk digunakan dengan CLI. Ini juga mengasumsikan bahwa Anda telah menginstal Helm ([Instruksi dapat ditemukan di sini](https://helm.sh/docs/intro/install/)).

## Tentukan Variabel Lingkungan

Langkah pertama dalam tutorial ini adalah menentukan variabel lingkungan.

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

## Buat grup sumber daya

Grup sumber daya adalah kontainer untuk sumber daya terkait. Semua sumber daya harus ditempatkan dalam grup sumber daya. Kami akan membuatnya untuk tutorial ini. Perintah berikut membuat grup sumber daya dengan parameter $MY_RESOURCE_GROUP_NAME dan $REGION yang ditentukan sebelumnya.

```bash
az group create --name $MY_RESOURCE_GROUP_NAME --location $REGION
```

Hasil:

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

## Membuat jaringan virtual dan subnet

Jaringan virtual adalah blok penyusun dasar untuk jaringan privat di Azure. Azure Virtual Network memungkinkan sumber daya Azure seperti VM untuk berkomunikasi satu sama lain dengan aman dan internet.

```bash
az network vnet create \
    --resource-group $MY_RESOURCE_GROUP_NAME \
    --location $REGION \
    --name $MY_VNET_NAME \
    --address-prefix $MY_VNET_PREFIX \
    --subnet-name $MY_SN_NAME \
    --subnet-prefixes $MY_SN_PREFIX
```

Hasil:

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

## Mendaftar ke Penyedia Sumber Daya Azure AKS

Pastikan bahwa penyedia Microsoft.OperationsManagement serta  Microsoft.OperationalInsights telah terdaftar di langganan Anda. Penyedia ini adalah penyedia sumber daya Azure yang diperlukan untuk mendukung [wawasan Kontainer](https://docs.microsoft.com/azure/azure-monitor/containers/container-insights-overview). Untuk memeriksa status pendaftaran, jalankan perintah berikut

```bash
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.OperationsManagement
az provider register --namespace Microsoft.OperationalInsights
```

## Buat Kluster AKS

Membuat kluster AKS menggunakan perintah az aks create dengan parameter --enable-addons monitoring untuk mengaktifkan insight Kontainer. Contoh berikut membuat kluster yang diaktifkan zona ketersediaan autoscaling.

Ini akan memakan waktu beberapa menit untuk menyelesaikannya.

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

## Menyambungkan ke kluster

Untuk mengelola kluster Kube, gunakan klien baris perintah Kube, kubectl. kubectl sudah diinstal jika Anda menggunakan Azure Cloud Shell.

1. Instal az aks CLI secara lokal menggunakan perintah az aks install-cli

   ```bash
   if ! [ -x "$(command -v kubectl)" ]; then az aks install-cli; fi
   ```

2. Konfigurasikan kubectl untuk terhubung ke kluster Kubernetes Anda menggunakan perintah az aks get-credentials. Jalankan perintah berikut:

   - Unduh informasi masuk dan konfigurasikan Kube CLI untuk menggunakannya.
   - Menggunakan ~/.kube/config, lokasi default untuk file konfigurasi Kubernetes. Tentukan lokasi berbeda untuk file konfigurasi Kubernetes Anda menggunakan argumen --file.

   > [!WARNING]
   > Ini akan menimpa kredensial yang ada dengan entri yang sama

   ```bash
   az aks get-credentials --resource-group $MY_RESOURCE_GROUP_NAME --name $MY_AKS_CLUSTER_NAME --overwrite-existing
   ```

3. Verifikasi koneksi ke kluster menggunakan perintah kubectl get. Perintah ini menampilkan daftar node kluster.

   ```bash
   kubectl get nodes
   ```

## Memasang Pengontrol Ingress NGINX

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

## Menyebarkan aplikasi

File manifes Kube menentukan status kluster yang diinginkan, seperti gambar kontainer mana yang akan dijalankan.

Dalam mulai cepat ini, Anda akan menggunakan manifes untuk membuat semua objek yang diperlukan untuk menjalankan Aplikasi Azure Vote. Manifes ini mencakup dua Penyebaran Kube:

- Sampel aplikasi Azure Vote Python.
- Instans Redis.

DuaLayanan Kubejuga dibuat:

- Layanan internal untuk instans Redis.
- Layanan eksternal untuk mengakses aplikasi Azure Vote dari internet.

Terakhir, sumber daya Ingress dibuat untuk merutekan lalu lintas ke aplikasi Azure Vote.

File YML aplikasi pemungutan suara pengujian sudah disiapkan. 

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

Untuk menyebarkan aplikasi ini, jalankan perintah berikut

```bash
kubectl apply -f azure-vote-start.yml
```

## Menguji aplikasi

Validasi bahwa aplikasi berjalan dengan mengunjungi ip publik atau url aplikasi. Url aplikasi dapat ditemukan dengan menjalankan perintah berikut:

> [!Note]
> Sering kali diperlukan waktu 2-3 menit agar POD dibuat dan situs dapat dijangkau melalui HTTP

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

Hasil:

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

## Menambahkan penghentian HTTPS ke domain kustom

Pada titik ini dalam tutorial, Anda memiliki aplikasi web AKS dengan NGINX sebagai pengontrol Ingress dan domain kustom yang dapat Anda gunakan untuk mengakses aplikasi Anda. Langkah selanjutnya adalah menambahkan sertifikat SSL ke domain sehingga pengguna dapat menjangkau aplikasi Anda dengan aman melalui HTTPS.

## Menyiapkan Cert Manager

Untuk menambahkan HTTPS, kami akan menggunakan Cert Manager. Cert Manager adalah alat sumber terbuka yang digunakan untuk mendapatkan dan mengelola sertifikat SSL untuk penyebaran Kubernetes. Cert Manager akan mendapatkan sertifikat dari berbagai Penerbit, penerbit publik populer maupun Penerbit privat, dan memastikan sertifikat valid dan terbaru, dan akan mencoba memperbarui sertifikat pada waktu yang dikonfigurasi sebelum kedaluwarsa.

1. Untuk menginstal cert-manager, kita harus terlebih dahulu membuat namespace layanan untuk menjalankannya. Tutorial ini akan menginstal cert-manager ke dalam namespace layanan cert-manager. Dimungkinkan untuk menjalankan cert-manager di namespace layanan yang berbeda, meskipun Anda harus membuat modifikasi pada manifes penyebaran.

   ```bash
   kubectl create namespace cert-manager
   ```

2. Kita sekarang dapat menginstal cert-manager. Semua sumber daya disertakan dalam satu file manifes YAML. Ini dapat diinstal dengan menjalankan hal berikut:

   ```bash
   kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.0/cert-manager.crds.yaml
   ```

3. Tambahkan label certmanager.k8s.io/disable-validation: "true" ke namespace layanan cert-manager dengan menjalankan yang berikut ini. Ini akan memungkinkan sumber daya sistem yang diperlukan cert-manager untuk bootstrap TLS untuk dibuat di namespacenya sendiri.

   ```bash
   kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
   ```

## Mendapatkan sertifikat melalui Bagan Helm

Helm adalah alat penyebaran Kubernetes untuk mengotomatiskan pembuatan, pengemasan, konfigurasi, dan penyebaran aplikasi dan layanan ke kluster Kubernetes.

Cert-manager menyediakan bagan Helm sebagai metode penginstalan kelas satu di Kubernetes.

1. Menambahkan repositori Jetstack Helm

   Repositori ini adalah satu-satunya sumber bagan cert-manager yang didukung. Ada beberapa cermin dan salinan lain di internet, tetapi itu sepenuhnya tidak resmi dan dapat menghadirkan risiko keamanan.

   ```bash
   helm repo add jetstack https://charts.jetstack.io
   ```

2. Memperbarui cache repositori Bagan Helm lokal

   ```bash
   helm repo update
   ```

3. Instal addon Cert-Manager melalui helm dengan menjalankan hal berikut:

   ```bash
   helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.7.0
   ```

4. Terapkan File YAML Penerbit Sertifikat

   ClusterIssuers adalah sumber daya Kubernetes yang mewakili otoritas sertifikat (CA) yang dapat menghasilkan sertifikat yang ditandatangani dengan mematuhi permintaan penandatanganan sertifikat. Semua sertifikat cert-manager memerlukan pengeluar sertifikat yang direferensikan dalam kondisi siap untuk mencoba memenuhi permintaan.
   Penerbit yang kami gunakan dapat ditemukan di `cluster-issuer-prod.yml file`
        
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

5. Upate Voting App Application untuk menggunakan Cert-Manager untuk mendapatkan Sertifikat SSL.

   File YAML lengkap dapat ditemukan di `azure-vote-nginx-ssl.yml`

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

## Telusuri Penyebaran AKS Anda Diamankan melalui HTTPS

Jalankan perintah berikut untuk mendapatkan titik akhir HTTPS untuk aplikasi Anda:

> [!Note]
> Sering kali diperlukan waktu 2-3 menit agar sertifikat SSL dapat diproposekan dan situs dapat dijangkau melalui HTTPS.

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

## Langkah berikutnya

- [Dokumentasi Azure Kubernetes Service](https://learn.microsoft.com/azure/aks/)
- [Membuat Azure Container Registry](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-prepare-acr?tabs=azure-cli)
- [Menskalakan Applciation Anda di AKS](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-scale?tabs=azure-cli)
- [Memperbarui aplikasi Anda di AKS](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-app-update?tabs=azure-cli)