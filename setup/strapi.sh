# https://docs.strapi.io/developer-docs/latest/setup-deployment-guides/deployment/hosting-guides/digitalocean.html
# https://strapi.io/blog/how-to-deploy-a-strapi-application

# enter the main directory
cd ..

# install nodejs
sudo apt-get install -y nodejs

# get the node version manager
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

# use npm 14
nvm install 14
nvm use 14

# update npx
npm update npx

# create a production-level strapi app for the cms
npx create-strapi-app@latest cms --quickstart

# install the dependencies
cd cms
npm install --production

# go out of the app
cd ..

# install pm2 (globally with -g)
npm install pm2

# start the server
NODE_ENV=production pm2 start server.js --name cms

# get nginx to host
sudo apt-get update
sudo apt-get install -y nginx

# continue here with the information from the docs
