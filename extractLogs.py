import paramiko
import json
from flask import Flask, Response

app = Flask(__name__)

# Function to establish SSH connection and execute commands
def ssh_command(hostname, username, password, command):
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Close the connection
        ssh.close()

        if error:
            return f"Error: {error}"
        return output
    except Exception as e:
        return f"SSH Connection Failed: {str(e)}"

# Function to fetch FetchConnector logs
def getFetchConnectorLogs(hostname, username, password, ref_id):
    folder_path = "apps/connectors/common-fetch-connector/'${sys:catalina.home}'/logs"  # Replace with the actual path
    file_name = "biller-fetch-app.log"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '/{ref_id}/{{if(!flag) {{flag=1; start=NR}}}} flag; /{ref_id}/{{last_match=NR}} END{{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"
    return ssh_command(hostname, username, password, command)

# Function to fetch PostConnector logs
def getPostConnectorLogs(hostname, username, password, ref_id):
    folder_path = "apps/connectors/common-post-connector/'${sys:catalina.home}'/logs"  # Replace with the actual path
    file_name = "biller-PostConnector-post-app.log"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '/{ref_id}/{{if(!flag) {{flag=1; start=NR}}}} flag; /{ref_id}/{{last_match=NR}} END{{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"
    return ssh_command(hostname, username, password, command)

# Function to fetch BillerConnect logs
def getConnectLogs(hostname, username, password, ref_id):
    folder_path = "apps/biller-connect/'${sys:catalina.home}'/logs"  # Replace with the actual path
    file_name = "biller-connect-app.log"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '/{ref_id}/{{if(!flag) {{flag=1; start=NR}}}} flag; /{ref_id}/{{last_match=NR}} END{{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"
    return ssh_command(hostname, username, password, command)

# Fourth function to fetch additional logs (similar template)
def getBBPSLogs(hostname, username, password, ref_id):
    folder_path = "apps/bbpsservice/logs"  # Replace with the actual path
    file_name = "catalina.out"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '{{lines[NR]=$0}} /{ref_id}/ {{if(!flag) {{flag=1; start=NR-3}}}}; /{ref_id}/ {{last_match=NR}} END {{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"    
    return ssh_command(hostname, username, password, command)

def getOfflineFetch(hostname, username, password, ref_id):
    folder_path = "apps/connectors/common-offline-fetch-connector/'${sys:catalina.home}'/logs"  # Replace with the actual path
    file_name = "offline-biller-fetch-app.log"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '{{lines[NR]=$0}} /{ref_id}/ {{if(!flag) {{flag=1; start=NR-3}}}}; /{ref_id}/ {{last_match=NR}} END {{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"    
    return ssh_command(hostname, username, password, command)


def getOfflinePost(hostname, username, password, ref_id):
    folder_path = "apps/connectors/common-offline-post-connector/'${sys:catalina.home}'/logs"  # Replace with the actual path
    file_name = "offlineBiller-PostConnector-post-app.log"  # Replace with the actual file name
    command = f"cd {folder_path} && tail -n 10000 {file_name} | awk '{{lines[NR]=$0}} /{ref_id}/ {{if(!flag) {{flag=1; start=NR-3}}}}; /{ref_id}/ {{last_match=NR}} END {{if(flag) {{for(i=start; i<=last_match; i++) print lines[i]}}}}'"    
    return ssh_command(hostname, username, password, command)


def strip_empty_lines(logs):
    """
    Removes empty lines from the logs.
    """
    if logs is None:
        return ""  # Return empty string if logs is None

    # Split logs into lines, filter out empty lines, and join them back
    lines = logs.splitlines()  # Split into lines
    non_empty_lines = [line for line in lines if line.strip()]  # Filter out empty lines
    cleaned_logs = "\n".join(non_empty_lines)  # Join non-empty lines with newline
    return cleaned_logs

# API endpoint to trigger the functions
@app.route('/getLogs/<refId>/<id>')
def get_logs(refId, id):
    hostname = "13.233.133.228"
    username = "green"
    password = "BtDh@71$jRst"
    
    try:
        # Convert id to integer for comparison
        log_id = int(id)
        
        # Select appropriate function based on id
        if log_id == 1:
            logs = getBBPSLogs(hostname, username, password, refId)
        elif log_id == 2:
            logs = getConnectLogs(hostname, username, password, refId)
        elif log_id == 3:
            logs = getFetchConnectorLogs(hostname, username, password, refId)
        elif log_id == 4:
            logs = getPostConnectorLogs(hostname, username, password, refId)
        elif log_id == 5:
            logs = getOfflineFetch(hostname, username, password, refId)
        elif log_id == 6:
            logs = getOfflinePost(hostname, username, password, refId)
        else:
            return "Invalid ID. Please use values 1-4.", 400
            
        return Response(strip_empty_lines(str(str(logs))), mimetype='text/plain')
        
    except ValueError:
        return "Invalid ID format. Please provide a number.", 400
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)