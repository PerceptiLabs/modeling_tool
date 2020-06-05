# Start keycloak server
Start the docker deamon and run the following command:
    ```
    docker run -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:10.0.1 
    ```

# Config keycloak server
Open new terminal and run the following command:
    ```
    ansible-playbook -i inventory.yml create_client.yml
    ```