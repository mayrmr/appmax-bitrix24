# Documentação: Integração Appmax → Bitrix24

## Objetivo
Automatizar a criação de contatos e negócios, determinar em pipeline de vendas onde será criado, e vincular o contato com o negócio criado dentro do Bitrix24 toda vez que uma compra for aprovada (paga) na Appmax.

## Tecnologias e recursos usados
- **Render**: Hospedagem da API webhook
- **Python + Flask**: Backend pra escutar e processar dados
- **Bitrix24 Webhook**: Alimentar dados, criar contatos e negócios via API
- **Appmax Webhook**: Envia o evento `OrderPaid` com os dados da compra para cadastro
- **GitHub**: Controle do projeto
- **Postman**: Testes locais

## Fluxo da Integração
1. Cliente realiza uma compra e paga.
2. Appmax reconhece o pagamento aprovado.
3. Appmax envia um `POST` para o endpoint:
   .
   https://appmax-bitrix.onrender.com/webhook/appmax
   .
4. O servidor Flask recebe os dados e trata:
   - Extrai informações do comprador (`customer`)
   - Verifica se já existe contato no Bitrix via CPF
   - Cria contato se não existir
   - Cria negócio vinculado ao contato com:
     - Nome do produto
     - Valor da compra
     - Número do pedido
   - Relaciona o negócio ao contato

## Lógica aplicada no backend
- Webhook deverá tratar apenas eventos `OrderPaid`
- Os campos personalizados do Bitrix que são usados para receber os dados são mapeados no dicionário `CAMPOS_PERSONALIZADOS`
- Os dados do JSON da Appmax são convertidos para o formato do Bitrix
- Os logs no terminal mostram:
  - Dados recebidos
  - Chaves do `customer`
  - Payloads tratados
  - Resultados de criação e vínculo

## Segurança e estabilidade
- Erros são tratados com `try/except`
- O campo obrigatório: CPF, gera erro 400 se ausente
- Suporte para testes com Postman
- Estrutura preparada para formatos diversos do JSON da Appmax

## Uso na Appmax
1. No painel da Appmax, vá em **Webhooks**
2. Configure o webhook com:
   .
   https://appmax-bitrix.onrender.com/webhook/appmax
   .
   - Evento: Pedido aprovado (`OrderPaid`)
   - Modelo de visualização da resposta (JSON): Modelo Padrão
   - Confirme as informações e salve
5. Realize uma compra com Pix e realize o pagamento
6. Verifique:
   - Logs no Render
   - Dados criados no Bitrix

## Dados trazidos para dentro do Bitrix
- Contato criado com:
  - Nome
  - E-mail
  - Telefone
  - CPF
  - Logradouro
  - Número
  - Complemento
  - Bairro
  - Cidade
  - CEP
  - Informações da fonte
- Negócio criado com:
  - Produto comprado
  - Valor pago
  - Número do pedido da Appmax
  - Informações da fonte
  - Vínculo com o contato

## Negócio criado
- Os negócios serão:
  - Criados dentro da pipeline *Venda Direta*
  - Etapa: *01. Integração Appmax*
- O Bitrix irá analisar o produto comprado e destinar o negócio à pipeline correta

## Status do Projeto
- Em funcionamento — API rodando em ambiente Render, recebendo Webhooks da Appmax e integrando automaticamente com o Bitrix24, onde passa a verificar os dados recebidos com base nos contatos existentes no banco de dados da empresa, se não for um cliente, o novo contato é gerado, criando o respectivo negócio, e vinculando ambos.  
- Em monitoramento e evolução contínua.

## Desenvolvimento
Desenvolvido por **May Romeiro Sartorelli**  
UX Designer • Desenvolvedora • Integração de Sistemas  
[mayrmrc@gmail.com](mailto:mayrmrc@gmail.com)  
[github.com/mayrmr](https://github.com/mayrmr)
