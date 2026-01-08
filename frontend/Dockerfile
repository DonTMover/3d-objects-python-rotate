FROM node:18-alpine

WORKDIR /usr/src/app

# copy templates and static assets into image
COPY ./src/templates ./templates
COPY ./src/static ./static

# install a simple static server
RUN npm install -g http-server

EXPOSE 3000
CMD ["http-server", "./templates", "-p", "3000", "-c-1"]
