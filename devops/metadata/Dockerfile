FROM blancahot/fennec-base:develop

#ENV
ENV COMPONENTS_ROOT=/app/components
ENV FENNEC_ROOT=/app/fennec
ENV WORKING_ROOT=/app/working_folder
ENV MAIN_TEMPLATE_FORM=/app/fennec/fennec_ui_components/forms/development-form.json
ENV FORM_TEMPLATES_FOLDER=/app/fennec/fennec_ui_components/templates
ENV AWS_ACCESS_KEY_ID=1
ENV AWS_SECRET_ACCESS_KEY=1
ENV AWS_DEFAULT_REGION=eu-west-2
ENV BACKEND_URL=http://localhost
ENV SOCKET_URL=http://localhost:9090


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

RUN sed -i '/backendUrl/c\  \"backendUrl\": \"$BACKEND_URL",' /usr/share/nginx/html/assets/config.json
RUN sed -i '/socketUrl/c\  \"socketUrl\": \"$SOCKET_URL",' /usr/share/nginx/html/assets/config.json
RUN echo "cat config.json" && cat /usr/share/nginx/html/assets/config.json

#Exposing node port	
EXPOSE 3000
EXPOSE 9090

CMD ["sh", "-c","pm2 start /app/backend/dist/src/index.js && nginx -g \"daemon off;\""]
