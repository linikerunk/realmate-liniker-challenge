FROM node:20-alpine

WORKDIR /app

# Instala as dependências do projeto
COPY package*.json ./
RUN npm install

# Copia o resto dos arquivos do projeto
COPY . .

# Expõe a porta que o Vite usa por padrão
EXPOSE 5173

# Comando para iniciar o servidor de desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
