FROM blancahot/fennec-base:develop

#ENV
ENV COMPONENTS_ROOT=/app/components
ENV FENNEC_ROOT=/app/fennec
ENV WORKING_ROOT=/app/working_folder
ENV MAIN_TEMPLATE_FORM=/app/fennec/fennec_ui_components/forms/development-form.json
ENV FORM_TEMPLATES_FOLDER=/app/fennec/fennec_ui_components/templates
ENV AWS_ACCESS_KEY_ID=1
ENV CLUSTER_NAMES=fennec,fennec-1
ENV REGIONS=eu-west-2,eu-west-1
ENV AWS_SECRET_ACCESS_KEY=1
ENV AWS_DEFAULT_REGION=eu-west-2
ENV BACKEND_URL=localhost:3000
ENV SOCKET_URL=localhost:9090
ENV DOMAIN_NAME=fennec.io
ENV ROUTE_53_ZONE_ID=Z09854781EPH1KKIXJ848,

# add webclient
COPY nginx.conf /etc/nginx/nginx.conf
COPY webclient/wizard /usr/share/nginx/html


# add backend
COPY backend/. /app/backend/.
RUN npm i pm2 -g

#add components
COPY components/. /app/.

#add fennec
COPY fennec/. /app/.

#install fennec module
RUN cd $FENNEC_ROOT \
  && ls \
  && pip3 install $FENNEC_ROOT/

COPY script.sh /app/.
RUN cd /app \
  && ls -lrt \
  && chmod +x script.sh 
  
  

#Exposing node port	
EXPOSE 80
EXPOSE 3000
EXPOSE 9090

ENTRYPOINT [ "/app/script.sh" ]

