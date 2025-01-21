# Overview

Executable Documentation (a.k.a **Exec Docs**) is a novel approach to simplify the evaluation and adoption of solutions provided with a CLI tool, such as Azure services. 

It achieves this by providing one-click and interactive learning experiences for deploying recommended architectures on Azure. 

These experiences utilize [Innovation Engine](https://github.com/Azure/InnovationEngine/tree/main), an open-source project that amplifies standard markdown language such that it can be executed step-by-step in an educational manner and tested via automated CI/CD pipelines.   

## Table of Contents

- [How to Write an Exec Doc](#how-to-write-an-exec-doc)
    - [Training Resources (Optional)](#training-resources-optional)
    - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Writing Requirements](#writing-requirements)
    - [Testing and Publishing](#testing-and-publishing)
- [Current Exec Docs Experience](#current-exec-docs-experience)
- [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs)
- [Contact Information for Exec Docs](#contact-information-for-exec-docs)

## How to Write an Exec Doc

Follow these steps in sequence to write an Exec Doc either by converting an existing Azure Doc i.e. building on top of the author's work or from scratch i.e. you are the author _(read the Notes in any step for more information)_:

### Training Resources (Optional)

**[Demo Workshop](https://microsoft-my.sharepoint.com/:v:/r/personal/carols_microsoft_com/Documents/Recordings/Exec%20Docs%20overview%20and%20hands-on%20training-20240806_170016-Meeting%20Recording.mp4?csf=1&web=1&e=jwpAHB&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifSwicGxheWJhY2tPcHRpb25zIjp7InN0YXJ0VGltZUluU2Vjb25kcyI6MjE5LjI3fX0%3D):** Link to the demo workshop that provides an overview of Exec Docs and a hands-on training session on how to write an Exec Doc. 

**[Presentation Deck](https://microsoft-my.sharepoint.com/:p:/p/namanparikh/EdxlQiyhGDhFmGcAUE9fejYB3r6ZzgLqWO3jZPK7fcnKgQ?e=PHcSQU)**: Link to the presentation deck used during the demo workshop covering important aspects of Exec Docs.

### Setup

1. Set up [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode) locally in your IDE such as VS Code and use the Linux terminal while writing the Exec Doc.

    >**Note:** Innovation Engine is a Linux-based tool and hence it is recommended to write Exec Docs in a Linux environment. Most doc authors use WSL in VS Code to write Exec Docs.

2. Set up the relevant repository in your local machine. This example covers the **azure-aks-docs-pr** repo.
    
    - Get access to the relevant repo in [MicrosoftDocs](https://github.com/MicrosoftDocs) in case it is private and/or you do not have access to it. 
    
    - Fork the [MicrosoftDocs/azure-aks-docs-pr](https://github.com/MicrosoftDocs/azure-aks-docs-pr) repo, which is where docs changes are made internally. Your fork URL would contain the following within: `<your_github_username>/azure-docs-pr`. [Guidance on how to fork a GitHub repo](https://review.learn.microsoft.com/en-us/help/common/contribute-fork-and-clone?branch=main#fork-the-repository)  

    - Clone a copy of your fork to your local machine. [Guidance on how to clone a forked GitHub repo](https://review.learn.microsoft.com/en-us/help/common/contribute-fork-and-clone?branch=main#clone-the-repository)

    - Make any changes to an existing/new Exec Doc in an IDE, such as VS Code. 
    
    - If you are converting an Azure Doc to Exec Doc and have a hard time finding the Azure doc in your fork, click the pencil icon in the public Azure doc and use the resultant filepath to find it in your fork.

    >**Note:** Push all changes to your fork as necessary
    
    >**Note:** You are not confined to use VS Code in WSL. You can use any IDE that supports markdown language. However, VS Code is recommended as it is the most common setup among doc authors.

    >**Note:** As part of [The Great Divide Project](https://microsoft.sharepoint.com/teams/AzCoreContent/SitePages/Great-Divide-.aspx), the Azure docs repo on GitHub is being divided into smaller repos for different CSA alignments. Make sure you are in the right repo for the doc you are looking for.

### Prerequisites

Check if all prerequisites below are met before writing the Exec Doc. ***If any of the below prerequisites are not met, then either add them to the Exec Doc in progress or find another valid doc that can fulfill them. Do not move to the next step until then***

3. Ensure your Exec Doc is a markdown file. 

    >**Note:** If you are converting an existing Azure Doc to an Exec Doc, you can either find it in your fork or copy the raw markdown content of the Azure Doc into a new markdown file in your local repo (this can be found by clicking "Raw" in the GitHub view of the Azure Doc). 

4. Ensure your Exec Doc is written with the LF line break type.

    **Example:** 

    ![LF VSCode](https://github.com/MicrosoftDocs/executable-docs/assets/146123940/3501cd38-2aa9-4e98-a782-c44ae278fc21)

    >**Note:** The button will appear according to the IDE you are using. For the VS Code IDE, you can check this by clicking on the LF/CLRF button at the bottom right corner of the screen.

5. Ensure all files that your Exec Doc references live under the same parent folder as your Exec Doc

    **Example:** 

    If your Exec Doc ***my-exec-doc.md*** references a script file ***my-script.yaml*** within, the script file should be in the same folder as the Exec Doc. 

    ```bash 
    ├── master-folder
    │   └── parent-folder
    │       ├── my-exec-doc.md 
    │       └── my-script.yaml 
    ``` 

6. Code blocks are used to provide examples, commands, or other code snippets in Exec Docs. They are distinguished by a triple backtick (```) at the start and end of the block. 

    Ensure that the Exec Doc contains at least 1 code block and every input code block's type in the Exec Doc is taken from this list: 

    - bash 
    - azurecli
    - azure-cli-interactive 
    - azurecli-interactive  

    **Example:** 

    ```bash 
    az group create --name $MY_RESOURCE_GROUP_NAME --location $REGION 
    ``` 

    >**Note:** This rule does not apply to output code blocks, which are used to display the results of commands, scripts, or other operations. These blocks help in illustrating what the expected output should look like. They include, but are not limited to, the following types: _output, json, yaml, console, text, and log._

    >**Note:** While Innovation Engine can _parse_ a code block of any type, given its current features, it can only _execute_ code blocks of the types above. So, it is important to ensure that the code blocks in your Exec Doc are of the types above. 

7. Headings are used to organize content in a document. The number of hashes indicates the level of the heading. For example, a single hash (#) denotes an h1 heading, two hashes (##) denote an h2 heading, and so on. Innovation Engine uses headings to structure the content of an Exec Doc and to provide a clear outline of the document's contents. 

    Ensure there is at least one h1 heading in the Exec Doc, denoted by a single hash (#) at the start of the line. 

    **Example:** 

    ```markdown 
    # Quickstart: Deploy an Azure Kubernetes Service (AKS) cluster using Azure CLI 
    ``` 

### Writing Requirements

8. Appropriately add metadata at the start of the Exec Doc. Here are some mandatory fields:

    - title = the title of the Exec Doc
    - description = the description of the Exec Doc
    - ms.topic = what kind of a doc it is e.g. article, blog, etc. 
    - ms.date = the date the Exec Doc was last updated by author 
    - author = author's GitHub username 
    - ms.author = author's username (e.g. Microsoft Alias)
    - **ms.custom = comma-separated list of tags to identify the Exec Doc (innovation-engine is the one tag that is mandatory in this list)**
        
    **Example:** 

    ```yaml 
    ---
    title: 'Quickstart: Deploy an Azure Kubernetes Service (AKS) cluster using Azure CLI' 
    description: Learn how to quickly deploy a Kubernetes cluster and deploy an application in Azure Kubernetes Service (AKS) using Azure CLI. 
    ms.topic: quickstart 
    ms.date: 11/11/2021 
    author: namanparikh 
    ms.author: namanaprikh 
    ms.custom: devx-track-azurecli, mode-api, innovation-engine, linux-related-content 
    ---
    ```

9. Environment variables are dynamic values that store configuration settings, system paths, and other information that can be accessed throughout a doc. By using environment variables, you can separate configuration details from the code, making it easier to manage and deploy applications in an environment like Exec Docs. 

    Declare environment variables _as they are being used_ in the Exec Doc using the export command. This is a best practice to ensure that the variables are accessible throughout the doc. 

    ### Example Exec Doc 1 - Environment variables declared at the _top_ of an Exec Doc, not declared as used
    
    **Environment Variables Section**

    We are at the start of the Exec Doc and are declaring environment variables that will be used throughout the doc. 

    ```bash
    export REGION="eastus"
    ```
    
    **Test Section**

    We are now in the middle of the Exec Doc and we will create a resource group.

    ```bash
    az group create --name "MyResourceGroup" --location $REGION
    ```
    
    ### Example Exec Doc 2 - Environment Variables declared as used** 
    
    **Test Section**

    We are in the middle of the Exec Doc and we will create a resource group. 

    ```bash  
    export REGION="eastus"
    export MY_RESOURCE_GROUP_NAME="MyResourceGroup"
    az group create --name $MY_RESOURCE_GROUP_NAME --location $REGION
    ``` 
    
    >**Note:** If you are converting an existing Azure Doc to an Exec Doc and the Azure Doc does not environment variables at all, it is an Exec Doc writing best practice to add them. Additionally, if the Azure Doc has environment variables but they are not declared as they are being used, it is recommended to update them to follow this best practice. 

    >**Note:** Don't have any spaces around the equal sign when declaring environment variables.

10. A major component of Exec Docs is automated infrastructure deployment on the cloud. While testing the doc, if you do not update relevant environment variable names, the doc will fail when run/executed more than once as the resource group or other resources will already exist from the previous runs. 

    Add a random suffix at the end of _relevant_ environment variable(s). The example below shows how this would work when you are creating a resource group.

    **Example:** 

    ```bash  
    export RANDOM_SUFFIX=$(openssl rand -hex 3)
    export REGION="eastus"
    az group create --name "MyResourceGroup$RANDOM_SUFFIX" --location $REGION
    ```

    >**Note:** Add a random suffix to relevant variables that are likely to be unique for each deployment, such as resource group names, VM names, and other resources that need to be uniquely identifiable. However, do not add a random suffix to variables that are constant or environment-specific, such as region, username, or configuration settings that do not change between deployments. 
    
    >**Note:** You can generate your own random suffix or use the one provided in the example above. The `openssl rand -hex 3` command generates a random 3-character hexadecimal string. This string is then appended to the resource group name to ensure that the resource group name is unique for each deployment.

11. In Exec Docs, result blocks are distinguished by a custom expected_similarity comment tag followed by a code block. These result blocks indicate to Innovation Engine what the minimum degree of similarity should be between the actual and the expected output of a code block (one which returns something in the terminal that is relevant to benchmark against). Learn More: [Result Blocks](https://github.com/Azure/InnovationEngine/blob/main/README.md#result-blocks). 

    Add result block(s) below code block(s) that you would want Innovation Engine to verify i.e. code block(s) which produce an output in the terminal that is relevant to benchmark against. Follow these steps when adding a result block below a code block for the first time:

    - Check if the code block does not already have a result block below it. If it does, ensure the result block is formatted correctly, as shown in the example below, and move to the next code block.
    - [Open Azure Cloudshell](https://ms.portal.azure.com/#cloudshell/) 
    - **[Optional]**: Set your active subscription to the one you are using to test Exec Docs. Ideally, this sub should have permissions to run commands in your tested Exec Docs. Run the following command: 

        ```bash
        az account set --subscription "<subscription name or id>"
        ``` 
    - Run the command in the code block in cloudshell. If it returns an output that you would want Innovation Engine to verify, copy the output from the terminal and paste it in a new code block below the original code block. The way a result code block should be formatted has been shown below, in this case for the command `az group create --name "MyResourceGroup123" --location eastus`.

        **Example:**
        ```markdown            
            Results: 

            <!-- expected_similarity=0.3 --> 

            ```JSON 
            {
                "id": "/subscriptions/abcabc-defdef-ghighi-jkljkl/resourceGroups/MyResourceGroup123",
                "location": "eastus",
                "managedBy": null,
                "name": "MyResourceGroup123",
                "properties": {
                    "provisioningState": "Succeeded"
                },
                "tags": null,
                "type": "Microsoft.Resources/resourceGroups"
            }
            ```
        ```
    - If you run into an error while executing a code block or the code block is running in an infinite loop, update the Exec Doc based on the error stack trace, restart/clear Cloudshell, and rerun the command block(s) from the start until you reach that command block. This is done to override any potential issues that may have occurred during the initial run. More guidance is given in the [FAQ section](#frequently-asked-questions-faqs) below.
    
    >**Note:** The expected similarity value is a percentage of similarity between 0 and 1 which specifies how closely the true output needs to match the template output given in the results block - 0 being no similarity, 1 being an exact match. If you are uncertain about the value, it is recommended to set the expected similarity to 0.3 i.e. 30% expected similarity to account for small variations. Once you have run the command multiple times and are confident that the output is consistent, you can adjust the expected similarity value accordingly.

    >**Note:** If you are executing a command in Cloudshell which references a yaml/json file, you would need to create the yaml/json file in Cloudshell and then run the command. This is because Cloudshell does not support the execution of commands that reference local files. You can add the file via the cat command or by creating the file in the Cloudshell editor. 

    >**Note:** Result blocks are not required but recommended for commands that return some output in the terminal. They help Innovation Engine verify the output of a command and act as checkpoints to ensure that the doc is moving in the right direction.

12. Redacting PII from the output helps protect sensitive information from being inadvertently shared or exposed. This is crucial for maintaining privacy, complying with data protection regulations, and furthering the company's security posture. 

    Ensure result block(s) have all the PII (Personally Identifiable Information) stricken out from them and replaced with x’s. 

    **Example:** 

    ```markdown
        Results: 

        <!-- expected_similarity=0.3 --> 

        ```JSON 
        { 
            "id": "/subscriptions/xxxxx-xxxxx-xxxxx-xxxxx/resourceGroups/MyResourceGroupxxx",
                "location": "eastus",
                "managedBy": null,
                "name": "MyResourceGroupxxx",
                "properties": {
                    "provisioningState": "Succeeded"
                },
                "tags": null,
                "type": "Microsoft.Resources/resourceGroups" 
        } 
        ```
    ```

    >**Note:** The number of x's used to redact PII need not be the same as the number of characters in the original PII. Furthermore, it is recommended not to redact the key names in the output, only the values containing the PII (which are usually strings).
    
    >**Note:** Here are some examples of PII in result blocks: Unique identifiers for resources, Email Addresses, Phone Numbers, IP Addresses, Credit Card Numbers, Social Security Numbers (SSNs), Usernames, Resource Names, Subscription IDs, Resource Group Names, Tenant IDs, Service Principal Names, Client IDs, Secrets and Keys.

13. If you are converting an existing Azure Doc to an Exec Doc and if the existing doc contains a "Delete Resources" (or equivalent section) comprising resource/other deletion command(s), remove the code blocks in that section or remove that section entirely 

    >**Note:** We remove commands from this section ***only*** in Exec Docs. This is because Innovation Engine executes all relevant command(s) that it encounters, inlcuding deleting the resources. That would be counterproductive to automated deployment of cloud infrastructure

### Testing and Publishing

14. Test the Exec Doc using Innovation Engine (IE) inside Azure Cloudshell 

    - [Open Azure Cloudshell](https://ms.portal.azure.com/#cloudshell/) 
    - **[Optional]**: Set your active subscription to the one you are using to test Exec Docs. Ideally, this sub should have permissions to run commands in your tested Exec Docs. Run the following command: 

        ```bash
        az account set --subscription "<subscription name or id>"
        ``` 
    - Install and set up the latest stable build of [Innovation Engine](https://github.com/Azure/InnovationEngine) (currently v0.2.0). Run the following command (ensure it is all run in one line): 
        ```bash
        curl –Lks https://raw.githubusercontent.com/Azure/InnovationEngine/v0.2.0/scripts/install_from_release.sh | /bin/bash -s -- v0.2.0 
        ``` 
    - Test your (Work In Progress) Exec Doc using Innovation Engine. Run the following command **(this command will automatically delete the resources at the end of the test)**: 

        ```bash
        ie test <URL to the raw Exec Doc markdown file>
        ``` 

        >**Note:** The URL to the raw Exec Doc markdown can be found by clicking "Raw" in the GitHub view of the Exec Doc. Also, ensure the GitHub repo is public otherwise Innovation Engine will not be able to access the raw markdown file.

        >**Note:** You can also test the Exec Doc by running the command "ie execute <URL to the raw Exec Doc markdown file>". This command will execute the code blocks in the Exec Doc but will not delete the resources at the end of the test. [Guidance on Innovation Engine's modes of operations](https://github.com/Azure/InnovationEngine?tab=readme-ov-file#modes-of-operation)
    
    - If you run into any errors, update the source doc in your upstream repo accordingly and retest it using Innovation Engine. For more guidance on troubleshooting errors, refer to the [FAQ section](#frequently-asked-questions-faqs) below. 

    >**Note:** Some code blocks may take a while to execute, especially if they are creating resources in Azure. You can finish other tasks while waiting for the code block to complete in the active Cloudshell window.

15. Submit and review the Exec Doc in the upstream repo once the doc passes all Innovation Engine tests
    - Create a PR in GitHub once the Exec Doc is ready to be uploaded, pointing to the upstream repo from your fork. [Guidance on creating a PR in GitHub from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork). 
    - You can use the example PR template below to reach out to the original author of the doc for review (in the PR description, email, or Teams message, etc.).

        **Example:**

        **Title:** _Making your Azure Doc executable!_

        _**Details:** Hello [author_name], \
        \
        I am submitting this PR to make the doc you have authored executable! Essentially, without any major content changes, this will make your doc accesssible, accurate, and actionable! And what is "this": Exec Docs (short for Executable Documentation) \
        \
        Exec Docs are documents that automate the deployment/maintenace of Azure resources using Azure CLI commands. This is a new initiative undertaken by the Azure Core Linux, Skilling, and Portal teams to simplify the evaluation and adoption of services for Linux on Azure customers. [Learn More Here!](https://github.com/MicrosoftDocs/executable-docs/blob/main/README.md)\
        \
        Once you get acquainted with Exec Docs, I would love to get your review on this doc. If you have any questions feel free to contact me or [Naman Parikh](mailto:namanparikh@microsoft.com)._

    - Assign the original Exec Doc author (if it is not you) as a reviewer to the PR. In most cases, this assignment should happen automatically and should include a reviewer from the Skilling team.
    - Add the comment ***#sign-off***  in the PR comments section once the Exec Doc is successfully reviewed. This will trigger the automated pipeline to merge the PR into the public repo.

16. Test the Exec Doc on the Azure Portal test environment once the PR is merged at source. The steps below explain the process with an [example Exec Doc](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli) that deploys an Azure Kubernetes Service (AKS) cluster using Azure CLI.
    - The [executable-docs repo](https://github.com/MicrosoftDocs/executable-docs/tree/main) is used to render the experience on Portal. A GitHub Action will sync your published Exec Doc in the executable-docs repo and create a PR to merge it in its main branch. Wait until you receive a notification from that PR: it will tag you and request you to test your Exec Doc before the merge happens

        **Example:**
      
      ![PR Template for Exec Docs Testing](https://github.com/user-attachments/assets/860e6153-5f95-4ebc-b774-2f30ef3a6219)
        
    - Click the URL in the PR description, which will take you to the test environment. Locate your Exec Doc from the cards page using doc metadata, etc.
    
        **Example:**

      ![Exec Docs Test Environment ](https://github.com/user-attachments/assets/8ab578a7-8b2f-4099-a34a-8824ba6bf50b)

    - Click either **Quick deployment** or **Guided deployment** and follow the instructions to test the Exec Doc
    - If the test fails, update the source doc in your upstream repo so that the GitHub action can sync the updated doc and allow you to test it. 
    
        >**Note:** Refer to the [FAQ section](#frequently-asked-questions-faqs) below for troubleshooting tips. If you are unable to resolve the issue, reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for help.
    - Once the test passes, send a screenshot of the post-deployment success page in the PR where you got tagged to test the Exec Doc. An example of the screenshot has been given below. After this gets approved, the PR will be merged into the main branch

        **Example:**

      ![Post Deployment Success Page Test Environment](https://github.com/user-attachments/assets/f002cd97-6bab-41a9-8c83-227e9b2da9cf)

17. The ***Deploy to Azure*** button is a clickable button that allows users to deploy the architecture described in the Exec Doc directly to their Azure subscription. This button is added to the source doc published on Microsoft Learn or elsewhere. 

    Add the ***Deploy to Azure*** button to the source doc published on [Microsoft Learn](https://learn.microsoft.com/en-us/) or elsewhere once the PR is merged in the [executable-docs repo](https://github.com/MicrosoftDocs/executable-docs/tree/main). Follow these steps to add the button:

    - Get the file path of your Exec Doc _relative_ to MicrosoftDocs/other GitHub organization. 
    
        **Example:** 

        If your source Exec Doc is located at `MicrosoftDocs/azure-docs/articles/aks/quick-kubernetes-deploy-cli.md` file, the file path for this purpose would be `azure-docs/articles/aks/quick-kubernetes-deploy-cli.md`

    - Add the code snippet (template given below) before the doc content starts (and after the table of contents if there is one). Replace all ***'/'*** signs in the file path with ***%2f*** for URL. So, for the example above, the file path would be `azure-docs%2farticles%2faks%2fquick-kubernetes-deploy-cli.md`

        **Deeplink Template:**
        ```markdown
        [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://ms.portal.azure.com/#view/Microsoft_Azure_CloudNative/SubscriptionSelectionPage.ReactView/isLearnMode~/true/referer/docs/tutorialKey/<add_file_path_of_Exec_Doc>)
        ```

        **Deeplink for Example Exec Doc:**
        ```markdown
        [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://ms.portal.azure.com/#view/Microsoft_Azure_CloudNative/SubscriptionSelectionPage.ReactView/isLearnMode~/true/referer/docs/tutorialKey/azure-docs%2farticles%2faks%2fquick-kubernetes-deploy-cli.md)
        ```

        **Example of Button in Live Exec Doc:**
        
      ![Deploy to Azure Button on Live Exec Doc](https://github.com/user-attachments/assets/3bfc1df7-8e33-4f22-b070-c365a6c3e917)

        >**Note:** The reason why we replace the '/' signs with '%2f' is because the '/' sign is a reserved character in URLs and needs to be encoded as '%2f' to be used in a URL.

## Current Exec Docs Experience

Exec Docs is a deployment vehicle that has different entry points into the experience. Here are the current entry points:

- [MS Learn](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli): A public facing Exec Doc on Microsoft Learn that enables users to create an Azure Kubernetes Service (AKS) cluster using Azure CLI.

- [GitHub](https://github.com/MicrosoftDocs/azure-aks-docs/blob/main/articles/aks/learn/quick-kubernetes-deploy-cli.md): The public GitHub repository where above mentioned Exec Doc lives.

- [Portal](https://ms.portal.azure.com/#view/Microsoft_Azure_CloudNative/TutorialsPage.ReactView): The Azure portal page where the current exec docs are displayed as cards.

- [Copilot](https://microsoft-my.sharepoint.com/:i:/p/namanparikh/EVOHA9I6mdtIvdnYjLtUg88B8g3_VlMDyXRQcEhTfie9SA?e=mkioB7): An example of Exec Docs being used by the Azure Copilot experience.

## Exec Docs E2E Publishing Pipeline

![Exec Docs Pipeline](https://github.com/user-attachments/assets/8102b631-634a-498c-a3a5-c099380acb07)

For questions or feedback on this pipeline, please reach out to the following people from the [Exec Docs Team](#contact-information-for-exec-docs):

- Skilling Questions: [Carol Smith](mailto:carols@microsoft.com)
- GitHub Actions Questions: [Naman Parikh](mailto:namanparikh@microsoft.com)
- Portal Questions: [PJ Singh](mailto:pjsingh@microsoft.com)

## Frequently Asked Questions (FAQs)

### Why is Exec Docs only limited to working in the CLI? Are there plans to expand to other tools?

Exec Docs runs on top of Innovation Engine. The way Innovation Engine is currently structured allows it to execute only CLI commands in a shell. Other deployment channels such as Portal are not yet in scope. However, there are plans to expand the capabilities of Innovation Engine to support other tools in the future.

### What are the most common errors you get when testing? How to troubleshoot them? 

Here are some common errors you may encounter when testing an Exec Doc and common troubleshooting steps to resolve them:

- **Error Code:** `SkuNotAvailable` \
  **Description:** This error occurs when the SKU you are trying to deploy is not available in the region you are deploying to. \
  **Troubleshooting:** Select a different region from the region selection dropdown before deployment begins. You can check the [Azure documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/troubleshooting/error-sku-not-available?tabs=azure-cli) to see which regions support the SKU you are trying to deploy.

- **Error Code:** `AuthorizationFailed` \
  **Description:** This error occurs when the client does not have sufficient permissions to perform the action. \
  **Troubleshooting:** Try running the Exec Doc under another subscription with higher permissions and/or verify that the service principal or user has the necessary permissions to perform the action under the current sub. You can assign the required role using the Azure portal, Azure CLI, or Azure PowerShell.

- **Error Code:** `ResourceQuotaExceeded` \
  **Description:** This error occurs when the resource quota for the subscription has been exceeded. \
  **Troubleshooting:** Check your subscription's resource quota and consider increasing the quota if necessary. You can request a quota increase through the Azure portal.

- **Error Code:** `no header found` \
  **Description:** This error occurs when the markdown file does not contain an H1 heading, corresponding to a title. Innovation Engine needs at least one heading to execute the code blocks within and display doc information in the CLI and Portal. Since the doc may or may not have subscetions, it uses the title heading i.e. the h1 heading as a minimum requirement.\
  **Troubleshooting:** Add an H1 heading to the markdown file, denoting the title of the doc. The heading should be denoted by a single hash (#) at the start of the line. 

- **Error Code:** `exit status 2` \
  **Description:** A common reason behind this error is the line endings in the markdown file are not consistent. Exec Doc markdown files should use LF (Line Feed) as line endings, not CRLF (Carriage Return Line Feed).\
  **Troubleshooting:** Ensure that the markdown file is saved with LF line endings. You can check this by clicking on the LF/CLRF button at the bottom right corner of the screen in your IDE, such as VS Code.

- **Error Code:** `File not found` or `The path does not exist` \
  **Description:** This error occurs when the file referenced in a command block does not exist in the same folder as the Exec Doc.\
  **Troubleshooting:** Ensure that all files referenced in the Exec Doc are in the same folder as the Exec Doc. If the file is not in the same folder, move it to the same folder as the Exec Doc.

Reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for further guidance if you are unable to resolve the issue. You can always ask Copilot for help as well.

### A command in my Exec Doc seems to be running forever. How do I stop it?

This may mean a command in your Exec Doc is running in an infinite loop. You can stop it during testing by pressing `Ctrl + C` in the terminal. Once the process is stopped, you can update the Exec Doc based on the error stack trace (and instructions in the source doc if you are converting it to an Exec Doc), restart/clear Cloudshell, and rerun the command block(s) from the start until you reach that command block. This is done to override any potential issues that may have occurred during the initial run.

### I am not the original author of the doc but I am converting it to an Exec Doc. Is the process any different?

No, the process remains the same whether you are the original author or you are updating a currently published doc to an Exec Doc. The only issue that may arise in the latter is if the original author is not available/takes too long to review the PR. In that case, you can reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for help.

### If I don’t know if I want to use WSL, where can I learn/read more? 

You can learn more about WSL and how to set it up in your IDE by visiting the [Windows Subsystem for Linux (WSL) documentation](https://learn.microsoft.com/en-us/windows/wsl/).

### What are examples of constant and environment-specific variables vs. Unique variables for each deployment? 

Essentially, constant and environment-specific variables do not change between deployments. Changing them would not make sense as they are used to store configuration settings, system paths, and other information that is consistent across deployments. Examples of these variables include Region, Username, Configuration settings, etc. 

Essentially, unique variables for each deployment are dynamic values that store information that is unique to each deployment. Changing them would make sense as they are used to store information that is unique to each deployment. Examples of these variables include Resource Group Names, VM Names, Other resources that need to be uniquely identifiable, etc.

### What will happen if I don’t follow the best practice of adding expected similarity blocks? 

If you don’t add expected similarity blocks, Innovation Engine will still execute the code blocks in the Exec Doc. However, it will not be able to verify the output of the command and act as checkpoints to ensure that the doc is moving in the right direction. For example, if your code block that is supposed to create a resource group instead contains `echo "Hello World"`, Innovation Engine will successfully execute this command but will not be able to verify the output. So, when you go to the next step in the Azure Portal test environment, it will fail as the resource group was not created.

### How do I know if I want to specify an Azure subscription when I’m testing my Exec Doc on Cloudshell using Innovation Engine? 

If you don't have a subscription already set or you have one but you don't know if it would be sufficient to test the Exec Doc, try running the Exec Doc using Innovation Engine and see if you encounter any errors. If you do, and the error contains "AuthorizationFailed" in the message, it is likely that the subscription has insufficient permissions to run the commands in the Exec Doc. In that case, you can set the subscription to another one within your tenant using the `az account set --subscription "<subscription name or id>"` command in Cloudshell. This command will set the active subscription to the one you are using to test Exec Docs. If the error persists, you can reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for help.

### Am I also required to loop in someone from the Exec Docs team to review when I have a PR ready? 

There are 2 PRs that need to be reviewed before the Exec Doc is merged into the main branch. The first PR is the one you create in the upstream repo once the Exec Doc is ready to be uploaded. The second PR is the one created by the GitHub Action in the executable-docs repo once the Exec Doc is merged in the upstream repo. 

For the first PR, if either the original doc author or someone from skilling is not tagged within, reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for help. The second PR should be automated and will automatically tag you to test your Exec Doc before it is merged. However, if you run into any edge cases there too, reach out to the [Exec Docs Team](#contact-information-for-exec-docs) for help.

## Contact Information for Exec Docs

- PM for Exec Docs E2E Experience: [Naman Parikh](mailto:namanparikh@microsoft.com)
- PM for Exec Docs Portal Experience: [Varun Desai](mailto:varun.desai@microsoft.com)
- PM for Innovation Engine: [Mitchell Bifeld](mailto:mbifeld@microsoft.com)
- Skilling & Content Developer for Exec Docs: [Carol Smith](mailto:carols@microsoft.com)
- Devs for Exec Docs: [PJ Singh](mailto:pjsingh@microsoft.com), [Aria Amini](mailto:ariaamini@microsoft.com), [Abhishek Bhombore](mailto:abhishek.bhombore@microsoft.com)
- Devs for Innovation Engine: [Vincenzo Marcella](mailto:vmarcella@microsoft.com), [Rahul Gupta](mailto:guptar@microsoft.com)

## Trademarks
This project may contain trademarks or logos for projects, products, or 
services. Authorized use of Microsoft trademarks or logos is subject to and 
must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must 
not cause confusion or imply Microsoft sponsorship. Any use of third-party 
trademarks or logos are subject to those third-party's policies.

## Microsoft Open Source Code of Conduct
This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
---
title: Deploy an AI model on Azure Kubernetes Service (AKS) with the AI toolchain operator (preview)
description: Learn how to enable the AI toolchain operator add-on on Azure Kubernetes Service (AKS) to simplify OSS AI model management and deployment.
ms.topic: article
ms.custom: azure-kubernetes-service, devx-track-azurecli
ms.date: 02/28/2024
author: schaffererin
ms.author: schaffererin
---

## Deploy an AI model on Azure Kubernetes Service (AKS) with the AI toolchain operator (preview)


The AI toolchain operator (KAITO) is a managed add-on for AKS that simplifies the experience of running OSS AI models on your AKS clusters. The AI toolchain operator automatically provisions the necessary GPU nodes and sets up the associated inference server as an endpoint server to your AI models. Using this add-on reduces your onboarding time and enables you to focus on AI model usage and development rather than infrastructure setup.

This article shows you how to enable the AI toolchain operator add-on and deploy an AI model on AKS.

[!INCLUDE [preview features callout](~/reusable-content/ce-skilling/azure/includes/aks/includes/preview/preview-callout.md)]



## Before you start this step


* This article assumes a basic understanding of Kubernetes concepts. For more information, see [Kubernetes core concepts for AKS](./concepts-clusters-workloads.md).
* For ***all hosted model inference images*** and recommended infrastructure setup, see the [KAITO GitHub repository](https://github.com/Azure/kaito).
* The AI toolchain operator add-on currently supports KAITO version **v0.1.0**, please make a note of this in considering your choice of model from the KAITO model repository.



## Prerequisites


* If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.
  * If you have multiple Azure subscriptions, make sure you select the correct subscription in which the resources will be created and charged using the [az account set](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest#az-account-set) command.

    > [!NOTE]
    > The subscription you use must have GPU VM quota.

* Azure CLI version 2.47.0 or later installed and configured. Run azure-cli                         2.65.0 *

core                              2.65.0 *
telemetry                          1.1.0

Extensions:
ai-examples                        0.2.5
ml                                2.30.1
ssh                                2.0.5

Dependencies:
msal                              1.31.0
azure-mgmt-resource               23.1.1

Python location '/usr/bin/python3.9'
Extensions directory '/home/pj/.azure/cliextensions'
Extensions system directory '/usr/lib/python3.9/site-packages/azure-cli-extensions'

Python (Linux) 3.9.19 (main, Aug 23 2024, 00:07:48) 
[GCC 11.2.0]

Legal docs and information: aka.ms/AzureCliLegal to find the version. If you need to install or upgrade, see [Install Azure CLI](/cli/azure/install-azure-cli).
* The Kubernetes command-line client, kubectl, installed and configured. For more information, see [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/).
* [Install the Azure CLI AKS preview extension](#install-the-azure-cli-preview-extension).
* [Register the AI toolchain operator add-on feature flag](#register-the-ai-toolchain-operator-add-on-feature-flag).



## Set up resource group


Set up a resource group with a random ID. Create an Azure resource group using the [az group create](https://learn.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-create) command.




```bash
export RANDOM_ID=15927e
export AZURE_RESOURCE_GROUP=myKaitoResourceGroup
export REGION=centralus
export CLUSTER_NAME=myClusterName

az group create     --name      --location  
```

## Install the Azure CLI preview extension


Install the Azure CLI preview extension using the [az extension add](https://learn.microsoft.com/en-us/cli/azure/extension?view=azure-cli-latest#az-extension-add) command. Then update the extension to make sure you have the latest version using the [az extension update](https://learn.microsoft.com/en-us/cli/azure/extension?view=azure-cli-latest#az-extension-update) command.




```bash
az extension add --name aks-preview
az extension update --name aks-preview
```

## Register the AI toolchain operator add-on feature flag


Register the AIToolchainOperatorPreview feature flag using the az feature register command.
It takes a few minutes for the registration to complete.




```bash
az feature register --namespace Microsoft.ContainerService --name AIToolchainOperatorPreview
```

## Verify the AI toolchain operator add-on registration


Verify the registration using the [az feature show](https://learn.microsoft.com/en-us/cli/azure/feature?view=azure-cli-latest#az-feature-show) command.




```bash
while true; do
    status=NotRegistered
    if [  == Registered ]; then
        break
    else
        sleep 15
    fi
done
```

## Create an AKS cluster with the AI toolchain operator add-on enabled


Create an AKS cluster with the AI toolchain operator add-on enabled using the [az aks create](https://learn.microsoft.com/en-us/cli/azure/aks?view=azure-cli-latest#az-aks-create) command with the  and  flags.




```bash
--enable-ai-toolchain-operator

--enable-oidc-issuer

az aks create --location      --resource-group      --name      --enable-oidc-issuer     --node-os-upgrade-channel SecurityPatch     --auto-upgrade-channel stable     --enable-ai-toolchain-operator     --generate-ssh-keys     --k8s-support-plan KubernetesOfficial
```

## Connect to your cluster


Configure kubectl controls the Kubernetes cluster manager.

 Find more information at: https://kubernetes.io/docs/reference/kubectl/

Basic Commands (Beginner):
  create          Create a resource from a file or from stdin
  expose          Take a replication controller, service, deployment or pod and expose it as a new Kubernetes service
  run             Run a particular image on the cluster
  set             Set specific features on objects

Basic Commands (Intermediate):
  explain         Get documentation for a resource
  get             Display one or many resources
  edit            Edit a resource on the server
  delete          Delete resources by file names, stdin, resources and names, or by resources and label selector

Deploy Commands:
  rollout         Manage the rollout of a resource
  scale           Set a new size for a deployment, replica set, or replication controller
  autoscale       Auto-scale a deployment, replica set, stateful set, or replication controller

Cluster Management Commands:
  certificate     Modify certificate resources
  cluster-info    Display cluster information
  top             Display resource (CPU/memory) usage
  cordon          Mark node as unschedulable
  uncordon        Mark node as schedulable
  drain           Drain node in preparation for maintenance
  taint           Update the taints on one or more nodes

Troubleshooting and Debugging Commands:
  describe        Show details of a specific resource or group of resources
  logs            Print the logs for a container in a pod
  attach          Attach to a running container
  exec            Execute a command in a container
  port-forward    Forward one or more local ports to a pod
  proxy           Run a proxy to the Kubernetes API server
  cp              Copy files and directories to and from containers
  auth            Inspect authorization
  debug           Create debugging sessions for troubleshooting workloads and nodes
  events          List events

Advanced Commands:
  diff            Diff the live version against a would-be applied version
  apply           Apply a configuration to a resource by file name or stdin
  patch           Update fields of a resource
  replace         Replace a resource by file name or stdin
  wait            Experimental: Wait for a specific condition on one or many resources
  kustomize       Build a kustomization target from a directory or URL

Settings Commands:
  label           Update the labels on a resource
  annotate        Update the annotations on a resource
  completion      Output shell completion code for the specified shell (bash, zsh, fish, or powershell)

Subcommands provided by plugins:

Other Commands:
  api-resources   Print the supported API resources on the server
  api-versions    Print the supported API versions on the server, in the form of "group/version"
  config          Modify kubeconfig files
  plugin          Provides utilities for interacting with plugins
  version         Print the client and server version information

Usage:
  kubectl [flags] [options]

Use "kubectl <command> --help" for more information about a given command.
Use "kubectl options" for a list of global command-line options (applies to all commands). to connect to your cluster using the [az aks get-credentials](https://learn.microsoft.com/en-us/cli/azure/aks?view=azure-cli-latest#az-aks-get-credentials) command.




```bash
kubectl

az aks get-credentials --resource-group  --name 
```

## Establish a federated identity credential


Create the federated identity credential between the managed identity, AKS OIDC issuer, and subject using the [az identity federated-credential create](https://learn.microsoft.com/en-us/cli/azure/identity/federated-credential?view=azure-cli-latest) command.




```bash
export MC_RESOURCE_GROUP=
export KAITO_IDENTITY_NAME=ai-toolchain-operator-
export AKS_OIDC_ISSUER=

az identity federated-credential create --name kaito-federated-identity     --identity-name      -g      --issuer      --subject system:serviceaccount:kube-system:kaito-gpu-provisioner     --audience api://AzureADTokenExchange
```

## Verify that your deployment is running


Restart the KAITO GPU provisioner deployment on your pods using the  command:




```bash
kubectl rollout restart

kubectl rollout restart deployment/kaito-gpu-provisioner -n kube-system
```

## Deploy a default hosted AI model


Deploy the Falcon 7B-instruct model from the KAITO model repository using the  command.




```bash
kubectl apply

kubectl apply -f https://raw.githubusercontent.com/Azure/kaito/main/examples/inference/kaito_workspace_falcon_7b-instruct.yaml
```

## Ask a question


Verify deployment done: .
Store IP: .
Ask question: 




```bash
kubectl get workspace workspace-falcon-7b-instruct -w

export SERVICE_IP=

kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- curl -X POST http:///chat -H accept: application/json -H Content-Type: application/json -d {"prompt":"YOUR QUESTION HERE"}

echo See last step for details on how to ask questions to the model.
```

## Next steps


For more inference model options, see the [KAITO GitHub repository](https://github.com/Azure/kaito).




