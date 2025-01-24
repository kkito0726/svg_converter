FROM node:current-alpine3.19

WORKDIR /user/src/client

COPY . .

RUN npm i \
 && npm run build

CMD [ "npm", "run", "preview" ]