# Dockerfile pour l'image TensorFlow

# Utiliser l'image officielle TensorFlow comme image de base
FROM tensorflow/tensorflow:latest

# (Facultatif) Copier le code source de votre application s'il est nécessaire
COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip

RUN pip install -r Docker/docker.tf.requirements.txt

EXPOSE 3000

# define environment variable
# ENV NAME World

# Commande par défaut pour démarrer votre application ou shell
# CMD ["bash", "./main.sh"]
# CMD ["bash", "./main.py"]




# build : docker build -t <image_name> -f <dockerfile_path> <build_context_path>
# docker build -t tf -f Docker/Dockerfile.tf .  # avec un dockerfile dans un dossier


# connect : docker exec --rm -it <container_name> /bin/bash  # --rm to remove container after exit
# docker run --rm -d -it tf /bin/bash

# run remove and detached : docker run --rm -idt <image_name>
# docker run --rm -idt tf

# options run
# -d: Détache le conteneur du terminal, c'est-à-dire qu'il s'exécute en arrière-plan.
# -p 4000:80: Mappe le port 4000 de l'hôte sur le port 80 du conteneur. Cela signifie que vous pouvez accéder au service en cours d'exécution dans le conteneur sur http://localhost:4000 sur votre machine hôte.


# connexion au container
# docker exec -it tf bash  # /bin/bash
# docker exec -it tf sh  # /bin/sh


