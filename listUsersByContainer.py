"""
This python script converts xml file content into oneliner and stores the output
 in a txt file .

Returns:
    CSV file with the following format [AccountId,EmailAddress,AccountUserAccess,ContainerId,ContainerName,ContainerUserAccess].

Example:
        $ python listUsersByContainer.py
"""

import csv
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service



def get_containers(service, account_id):
    """Get all containers Ids and container names for an account and return a python dictionary.

    Args:
        service: The service that is connected to the specified API.
        account_id: the Google Tag Manager account id to pull the containers for.

    Returns:
        A python dictionary with the container Ids as keys and the container names as values.
    """

    containers_dict = {}

    container_data = service.accounts().containers().list(accountId=account_id).execute()

    for container in container_data.get('containers'):
        containerId = container.get('containerId')
        containerName = container.get('name')
        containers_dict[containerId] = containerName

    return containers_dict


def get_user_data_list(service):
    """Get all user emails addresses and permissions for all GTM account and its containers.

    Args:
        service: The service that is connected to the specified API.

    Returns:
        A list of lists [[AccountId], [EmailAddress], [AccountUserAccess], [ContainerId], [ContainerName], [ContainerUserAccess]].
    """

    list_accountId = ['AccountId']
    list_accountName = ['AccountName']
    list_userEmail = ['EmailAddress']
    list_accountUserAccess = ['AccountUserAccess']
    list_containerId = ['ContainerId']
    list_containerName = ['ContainerName']
    list_containerUserAccess = ['ContainerUserAccess']



    # Get a list of all Google Tag Manager accounts the service account has access to
    accounts = service.accounts().list().execute()

    # Check if there is any account with access for the selected user
    if accounts.get('accounts'):
        # Search all accounts the user_account has access to
        for account in accounts.get('accounts'):
            # Get account name and account Id
            account_name = account.get('name')
            account_id = account.get('accountId')
            user_access_all_data = service.accounts().permissions().list(accountId=account_id).execute()
            containers_dict = get_containers(service, account_id)

            # Check if there are any users with access to the account
            if user_access_all_data.get('userAccess'):
                # Search all Web Properties the user_account has access to
                for user_access in user_access_all_data.get('userAccess'):
                    # Get user access details
                    userEmail = user_access.get('emailAddress')
                    accountUserAccess = user_access.get('accountAccess').get('permission')

                    if user_access.get('containerAccess'):
                        for container in user_access.get('containerAccess'):
                            containerId = container.get('containerId')
                            containerName = containers_dict.get(containerId)
                            containerUserAccess = container.get('permission')

                            # Append accountId, accountName, userEmail, accountUserAccess, containerId, containerName and containerUserAccess values to python lists
                            list_accountId.append(account_id)
                            list_accountName.append(account_name)
                            list_userEmail.append(userEmail)
                            list_accountUserAccess.append(accountUserAccess)
                            list_containerId.append(containerId)
                            list_containerName.append(containerName)
                            list_containerUserAccess.append(containerUserAccess)

    # Final python list which includes all retrieved user data from Google Analytics
    final_user_data_list = [list_accountId, list_accountName, list_userEmail, list_accountUserAccess, list_containerId, list_containerName, list_containerUserAccess]

    return final_user_data_list


def print_table_to_csv(data_list, filename):
    """Print input list of lists in a csv format in the same folder as this scripts.

    Args:
        data_list: A list of lists populated with data.
        filename: A file name in string format used for the output file.

    Returns:
        None
    """
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        for iter in range(len(data_list[0])):
            writer.writerow([x[iter] for x in data_list])


def main():
    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/tagmanager.manage.users', 'https://www.googleapis.com/auth/tagmanager.edit.containers',
             'https://www.googleapis.com/auth/tagmanager.readonly']
    key_file_location = 'P:\service_acccount_keys\my_project-c1c9c02d2c87.json'

    output_csv_filename = "GoogleTagManagerUserDataList.csv"

    # Authenticate and construct service.
    service = get_service(
            api_name='tagmanager',
            api_version='v1',
            scopes=scope,
            key_file_location=key_file_location)

    final_user_data_list = get_user_data_list(service)
    print_table_to_csv(final_user_data_list, output_csv_filename)


if __name__ == '__main__':
    main()