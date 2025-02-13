# WELCOME TO ADA - AI DOCUMENTATION ASSISTANT

import os
import sys
import subprocess
import shutil
import pkg_resources
import csv
import time
from datetime import datetime
from openai import AzureOpenAI
from collections import defaultdict

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = 'gpt-4o'

REQUIRED_PACKAGES = [
    'openai',
    'azure-identity',
    'requests',
]

for package in REQUIRED_PACKAGES:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

system_prompt = """Exec Docs is a vehicle that transforms standard markdown into interactive, executable learning content, allowing code commands within the document to be run step-by-step or “one-click”. This is powered by the Innovation Engine, an open-source CLI tool that powers the execution and testing of these markdown scripts and can integrate with automated CI/CD pipelines. You are an Exec Doc writing expert. You will either write a new exec doc from scratch if no doc is attached or update an existing one if it is attached. You must adhere to the following rules while presenting your output:

### Prerequisites

Check if all prerequisites below are met before writing the Exec Doc. ***If any of the below prerequisites are not met, then either add them to the Exec Doc in progress or find another valid doc that can fulfill them. Do not move to the next step until then***

1. Ensure your Exec Doc is a markdown file. 

    >**Note:** If you are converting an existing Azure Doc to an Exec Doc, you can either find it in your fork or copy the raw markdown content of the Azure Doc into a new markdown file in your local repo (this can be found by clicking "Raw" in the GitHub view of the Azure Doc). 

2. Ensure your Exec Doc is written with the LF line break type.

    **Example:** 

    ![LF VSCode](https://github.com/MicrosoftDocs/executable-docs/assets/146123940/3501cd38-2aa9-4e98-a782-c44ae278fc21)

    >**Note:** The button will appear according to the IDE you are using. For the VS Code IDE, you can check this by clicking on the LF/CLRF button at the bottom right corner of the screen.

3. Ensure all files that your Exec Doc references live under the same parent folder as your Exec Doc

    **Example:** 

    If your Exec Doc ***my-exec-doc.md*** references a script file ***my-script.yaml*** within, the script file should be in the same folder as the Exec Doc. 

    ```bash 
    ├── master-folder
    │   └── parent-folder
    │       ├── my-exec-doc.md 
    │       └── my-script.yaml 
    ``` 

4. Code blocks are used to provide examples, commands, or other code snippets in Exec Docs. They are distinguished by a triple backtick (```) at the start and end of the block. 

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

5. Headings are used to organize content in a document. The number of hashes indicates the level of the heading. For example, a single hash (#) denotes an h1 heading, two hashes (##) denote an h2 heading, and so on. Innovation Engine uses headings to structure the content of an Exec Doc and to provide a clear outline of the document's contents. 

    Ensure there is at least one h1 heading in the Exec Doc, denoted by a single hash (#) at the start of the line. 

    **Example:** 

    ```markdown 
    # Quickstart: Deploy an Azure Kubernetes Service (AKS) cluster using Azure CLI 
    ``` 

### Writing Requirements

6. Ensure that the Exec Doc does not include any commands or descriptions related to logging into Azure (e.g., `az login`) or setting the subscription ID. The user is expected to have already logged in to Azure and set their subscription beforehand. Do not include these commands or any descriptions about them in the Exec Doc.

7. Ensure that the Exec Doc does not require any user interaction during its execution. The document should not include any commands or scripts that prompt the user for input or expect interaction with the terminal. All inputs must be predefined and handled automatically within the script.

7. Appropriately add metadata at the start of the Exec Doc. Here are some mandatory fields:

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

7. Ensure the environment variable names are not placeholders i.e. <> but have a certain generic, useful name. For the location/region parameter, default to "WestUS2" or "centralindia". Additionally, appropriately add descriptions below every section explaining what is happening in that section in crisp but necessary detail so that the user can learn as they go.

8. Don't start and end your answer with ``` backticks!!! Don't add backticks to the metadata at the top!!!. 

8. Ensure that any info, literally any info whether it is a comment, tag, description, etc., which is not within a code block remains unchanged. Preserve ALL details of the doc.

8. Environment variables are dynamic values that store configuration settings, system paths, and other information that can be accessed throughout a doc. By using environment variables, you can separate configuration details from the code, making it easier to manage and deploy applications in an environment like Exec Docs. 

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

9. A major component of Exec Docs is automated infrastructure deployment on the cloud. While testing the doc, if you do not update relevant environment variable names, the doc will fail when run/executed more than once as the resource group or other resources will already exist from the previous runs. 

    Add a random suffix at the end of _relevant_ environment variable(s). The example below shows how this would work when you are creating a resource group.

    **Example:** 

    ```bash  
    export RANDOM_SUFFIX=$(openssl rand -hex 3)
    export REGION="eastus"
    az group create --name "MyResourceGroup$RANDOM_SUFFIX" --location $REGION
    ```

    >**Note:** Add a random suffix to relevant variables that are likely to be unique for each deployment, such as resource group names, VM names, and other resources that need to be uniquely identifiable. However, do not add a random suffix to variables that are constant or environment-specific, such as region, username, or configuration settings that do not change between deployments. 
    
    >**Note:** You can generate your own random suffix or use the one provided in the example above. The `openssl rand -hex 3` command generates a random 3-character hexadecimal string. This string is then appended to the resource group name to ensure that the resource group name is unique for each deployment.

10. In Exec Docs, result blocks are distinguished by a custom expected_similarity comment tag followed by a code block. These result blocks indicate to Innovation Engine what the minimum degree of similarity should be between the actual and the expected output of a code block (one which returns something in the terminal that is relevant to benchmark against). Learn More: [Result Blocks](https://github.com/Azure/InnovationEngine/blob/main/README.md#result-blocks). 

    Add result block(s) below code block(s) that you would want Innovation Engine to verify i.e. code block(s) which produce an output in the terminal that is relevant to benchmark against. Follow these steps when adding a result block below a code block for the first time:

    - Check if the code block does not already have a result block below it. If it does, ensure the result block is formatted correctly, as shown in the example below, and move to the next code block.
    - [Open Azure Cloudshell](https://ms.portal.azure.com/#cloudshell/) 
    - **[Optional]**: Set your active subscription to the one you are using to test Exec Docs. Ideally, this sub should have permissions to run commands in your tested Exec Docs. Run the following command: 

        ```bash
        az account set --subscription "<subscription name or id>"
        ``` 
    - Run the command in the code block in cloudshell. If it returns an output that you would want Innovation Engine to verify, copy the output from the terminal and paste it in a new code block below the original code block. The way a result code block should be formatted has been shown below, in this case for the command [az group create --name "MyResourceGroup123" --location eastus](http://_vscodecontentref_/1).

        **Example:**
        ```markdown            
            Results: 

            <!-- expected_similarity=0.3 --> 

            ```JSON 
            {{
                "id": "/subscriptions/abcabc-defdef-ghighi-jkljkl/resourceGroups/MyResourceGroup123",
                "location": "eastus",
                "managedBy": null,
                "name": "MyResourceGroup123",
                "properties": {{
                    "provisioningState": "Succeeded"
                }},
                "tags": null,
                "type": "Microsoft.Resources/resourceGroups"
            }}
            ```
        ```
    - If you run into an error while executing a code block or the code block is running in an infinite loop, update the Exec Doc based on the error stack trace, restart/clear Cloudshell, and rerun the command block(s) from the start until you reach that command block. This is done to override any potential issues that may have occurred during the initial run. More guidance is given in the [FAQ section](#frequently-asked-questions-faqs) below.
    
    >**Note:** The expected similarity value is a percentage of similarity between 0 and 1 which specifies how closely the true output needs to match the template output given in the results block - 0 being no similarity, 1 being an exact match. If you are uncertain about the value, it is recommended to set the expected similarity to 0.3 i.e. 30% expected similarity to account for small variations. Once you have run the command multiple times and are confident that the output is consistent, you can adjust the expected similarity value accordingly.

    >**Note:** If you are executing a command in Cloudshell which references a yaml/json file, you would need to create the yaml/json file in Cloudshell and then run the command. This is because Cloudshell does not support the execution of commands that reference local files. You can add the file via the cat command or by creating the file in the Cloudshell editor. 

    >**Note:** Result blocks are not required but recommended for commands that return some output in the terminal. They help Innovation Engine verify the output of a command and act as checkpoints to ensure that the doc is moving in the right direction.

11. Redacting PII from the output helps protect sensitive information from being inadvertently shared or exposed. This is crucial for maintaining privacy, complying with data protection regulations, and furthering the company's security posture. 

    Ensure result block(s) have all the PII (Personally Identifiable Information) stricken out from them and replaced with x’s. 

    **Example:** 

    ```markdown
        Results: 

        <!-- expected_similarity=0.3 --> 

        ```JSON 
        {{ 
            "id": "/subscriptions/xxxxx-xxxxx-xxxxx-xxxxx/resourceGroups/MyResourceGroupxxx",
                "location": "eastus",
                "managedBy": null,
                "name": "MyResourceGroupxxx",
                "properties": {{
                    "provisioningState": "Succeeded"
                }},
                "tags": null,
                "type": "Microsoft.Resources/resourceGroups" 
        }} 
        ```
    ```

    >**Note:** The number of x's used to redact PII need not be the same as the number of characters in the original PII. Furthermore, it is recommended not to redact the key names in the output, only the values containing the PII (which are usually strings).
    
    >**Note:** Here are some examples of PII in result blocks: Unique identifiers for resources, Email Addresses, Phone Numbers, IP Addresses, Credit Card Numbers, Social Security Numbers (SSNs), Usernames, Resource Names, Subscription IDs, Resource Group Names, Tenant IDs, Service Principal Names, Client IDs, Secrets and Keys.

12. If you are converting an existing Azure Doc to an Exec Doc and if the existing doc contains a "Delete Resources" (or equivalent section) comprising resource/other deletion command(s), remove the code blocks in that section or remove that section entirely 

    >**Note:** We remove commands from this section ***only*** in Exec Docs. This is because Innovation Engine executes all relevant command(s) that it encounters, inlcuding deleting the resources. That would be counterproductive to automated deployment of cloud infrastructure

## WRITE AND ONLY GIVE THE EXEC DOC USING THE ABOVE RULES FOR THE FOLLOWING WORKLOAD: """

def install_innovation_engine():
    if shutil.which("ie") is not None:
        print("\nInnovation Engine is already installed.\n")
        return
    print("\nInstalling Innovation Engine...\n")
    subprocess.check_call(
        ["curl", "-Lks", "https://raw.githubusercontent.com/Azure/InnovationEngine/v0.2.3/scripts/install_from_release.sh", "|", "/bin/bash", "-s", "--", "v0.2.3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("\nInnovation Engine installed successfully.\n")

def get_last_error_log():
    log_file = "ie.log"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()
            error_index = None
            for i in range(len(lines) - 1, -1, -1):
                if "level=error" in lines[i]:
                    error_index = i
                    break
            if error_index is not None:
                return "".join(lines[error_index:])
    return "No error log found."

def remove_backticks_from_file(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    if lines and "```" in lines[0]:
        lines = lines[1:]

    if lines and "```" in lines[-1]:
        lines = lines[:-1]

    # Remove backticks before and after the metadata section
    if lines and "---" in lines[0]:
        for i in range(1, len(lines)):
            if "---" in lines[i]:
                if "```" in lines[i + 1]:
                    lines = lines[:i + 1] + lines[i + 2:]
                break

    with open(file_path, "w") as f:
        f.writelines(lines)

def log_data_to_csv(data):
    file_exists = os.path.isfile('execution_log.csv')
    with open('execution_log.csv', 'a', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Type', 'Input', 'Output', 'Number of Attempts', 'Errors Encountered', 'Execution Time (in seconds)', 'Success/Failure']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def main():
    print("\nWelcome to ADA - AI Documentation Assistant!\n")
    print("This tool helps you write and troubleshoot Executable Documents efficiently!\n")
    
    user_input = input("Please enter the path to your markdown file for conversion or describe your intended workload: ")

    if os.path.isfile(user_input) and user_input.endswith('.md'):
        input_type = 'file'
        with open(user_input, "r") as f:
            input_content = f.read()
    else:
        input_type = 'workload_description'
        input_content = user_input

    install_innovation_engine()

    max_attempts = 11
    attempt = 1
    if input_type == 'file':
        output_file = f"converted_{os.path.splitext(os.path.basename(user_input))[0]}.md"
    else:
        output_file = "generated_exec_doc.md"

    start_time = time.time()
    errors_encountered = []

    while attempt <= max_attempts:
        if attempt == 1:
            print(f"\n{'='*40}\nAttempt {attempt}: Generating Exec Doc...\n{'='*40}")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_content}
                ]
            )
            output_file_content = response.choices[0].message.content
            with open(output_file, "w") as f:
                f.write(output_file_content)
        else:
            print(f"\n{'='*40}\nAttempt {attempt}: Generating corrections based on error...\n{'='*40}")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_content},
                    {"role": "assistant", "content": output_file_content},
                    {"role": "user", "content": f"The following error(s) have occurred during testing:\n{errors_text}\nPlease carefully analyze these errors and make necessary corrections to the document to prevent them from happening again. Try to find different solutions if the same errors keep occurring. \nGiven that context, please think hard and don't hurry. I want you to correct the converted document in ALL instances where this error has been or can be found. Then, correct ALL other errors apart from this that you see in the doc. ONLY GIVE THE UPDATED DOC, NOTHING ELSE"}
                ]
            )
            output_file_content = response.choices[0].message.content
            with open(output_file, "w") as f:
                f.write(output_file_content)

        remove_backticks_from_file(output_file)

        print(f"\n{'-'*40}\nRunning Innovation Engine tests...\n{'-'*40}")
        try:
            result = subprocess.run(["ie", "test", output_file], capture_output=True, text=True, timeout=660)
        except subprocess.TimeoutExpired:
            print("The 'ie test' command timed out after 11 minutes.")
            errors_encountered.append("The 'ie test' command timed out after 11 minutes.")
            attempt += 1
            continue  # Proceed to the next attempt
        if result.returncode == 0:
            print(f"\n{'*'*40}\nAll tests passed successfully.\n{'*'*40}")
            success = True
            print(f"\n{'='*40}\nProducing Exec Doc...\n{'='*40}")
            if input_type == 'file':
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        f"The following errors have occurred during testing:\n{errors_text}\n{additional_instruction}\nPlease carefully analyze these errors and make necessary corrections to the document to prevent them from happening again. ONLY GIVE THE UPDATED DOC, NOTHING ELSE"
                    ]
                )
            output_file_content = response.choices[0].message.content
            with open(output_file, "w") as f:
                f.write(output_file_content)
            remove_backticks_from_file(output_file)
            break
        else:
            print(f"\n{'!'*40}\nTests failed. Analyzing errors...\n{'!'*40}")
            error_log = get_last_error_log()
            errors_encountered.append(error_log.strip())
            errors_text = "\n\n ".join(errors_encountered)
            # Process and count error messages
            error_counts = defaultdict(int)
            for error in errors_encountered:
                lines = error.strip().split('\n')
                for line in lines:
                    if 'Error' in line or 'Exception' in line:
                        error_counts[line] += 1

            # Identify repeating errors
            repeating_errors = {msg: count for msg, count in error_counts.items() if count > 1}

            # Prepare additional instruction if there are repeating errors
            if repeating_errors:
                repeating_errors_text = "\n".join([f"Error '{msg}' has occurred {count} times." for msg, count in repeating_errors.items()])
                additional_instruction = f"The following errors have occurred multiple times:\n{repeating_errors_text}\nPlease consider trying a different approach to fix these errors."
            else:
                additional_instruction = ""
            print(f"\nError: {error_log.strip()}")
            attempt += 1
            success = False

    if attempt > max_attempts:
        print(f"\n{'#'*40}\nMaximum attempts reached without passing all tests.\n{'#'*40}")

    end_time = time.time()
    execution_time = end_time - start_time

    log_data = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Type': input_type,
        'Input': user_input,
        'Output': output_file,
        'Number of Attempts': attempt-1,
        'Errors Encountered': "\n\n ".join(errors_encountered),
        'Execution Time (in seconds)': execution_time,
        'Success/Failure': "Success" if success else "Failure"
    }

    log_data_to_csv(log_data)

    print(f"\nThe updated file is stored at: {output_file}\n")

if __name__ == "__main__":
    main()
