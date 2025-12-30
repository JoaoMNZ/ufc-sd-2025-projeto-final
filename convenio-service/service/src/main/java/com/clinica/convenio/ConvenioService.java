package com.clinica.convenio;

import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import org.json.JSONObject;

public class ConvenioService {
    private static final int PORT = 5003;
    private ExecutorService threadPool;

    public ConvenioService() {
        this.threadPool = Executors.newFixedThreadPool(10);
    }

    public void start() {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Serviço de Validação de Convênio iniciado na porta " + PORT);
            System.out.println("Aguardando requisições de validação...\n");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                threadPool.execute(() -> handleClient(clientSocket));
            }
        } catch (IOException e) {
            System.err.println("Erro no servidor: " + e.getMessage());
        }
    }

    private void handleClient(Socket clientSocket) {
        try (
                BufferedReader in = new BufferedReader(
                        new InputStreamReader(clientSocket.getInputStream())
                );
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)
        ) {
            String requestLine = in.readLine();
            if (requestLine == null) return;

            System.out.println("Requisição recebida: " + requestLine);
            JSONObject request = new JSONObject(requestLine);
            String action = request.getString("action");

            JSONObject response = processRequest(action, request);
            out.println(response.toString());
            System.out.println("Resposta enviada: " + response.toString() + "\n");

        } catch (Exception e) {
            System.err.println("Erro ao processar cliente: " + e.getMessage());
            e.printStackTrace();
        } finally {
            try {
                clientSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private JSONObject processRequest(String action, JSONObject request) {
        try {
            return switch (action) {
                case "validar_pagamento" -> validarPagamento(request);
                default -> createErrorResponse("Ação inválida: " + action);
            };
        } catch (Exception e) {
            e.printStackTrace();
            return createErrorResponse("Erro ao processar: " + e.getMessage());
        }
    }

    /**
     * - Lógica determinística:
     * - CONVENIO: Válido se tamanho do nome do convênio for PAR
     * - PARTICULAR: Válido se último dígito do cartão for PAR
     */
    private JSONObject validarPagamento(JSONObject request) {
        int agendamentoId = request.getInt("agendamento_id");
        int pacienteId = request.getInt("paciente_id");
        String tipoPagamento = request.getString("tipo_pagamento").toUpperCase();

        boolean aprovado;
        String mensagem;
        String detalhes = "";

        // Lógica determinística baseada no tipo de pagamento
        if (tipoPagamento.equals("CONVENIO")) {
            String nomeConvenio = request.getString("convenio_nome");
            int tamanhoNome = nomeConvenio.length();
            aprovado = (tamanhoNome % 2 == 0); // PAR = válido

            detalhes = String.format("Convênio: %s (tamanho: %d)", nomeConvenio, tamanhoNome);
            mensagem = aprovado
                    ? "Convênio validado com sucesso - Nome possui tamanho PAR"
                    : "Convênio rejeitado - Nome possui tamanho ÍMPAR";

            System.out.println(String.format(
                    "Validação CONVÊNIO | Agendamento #%d | %s | Tamanho: %d (%s) | Resultado: %s",
                    agendamentoId, nomeConvenio, tamanhoNome,
                    (tamanhoNome % 2 == 0) ? "PAR" : "ÍMPAR",
                    aprovado ? "APROVADO" : "REJEITADO"
            ));

        } else if (tipoPagamento.equals("PARTICULAR")) {
            String numeroCartao = request.getString("numero_cartao");
            char ultimoDigito = numeroCartao.charAt(numeroCartao.length() - 1);
            int digitoInt = Character.getNumericValue(ultimoDigito);
            aprovado = (digitoInt % 2 == 0); // PAR = válido

            // Mascara o cartão para segurança (mostra apenas últimos 4 dígitos)
            String cartaoMascarado = "**** **** **** " + numeroCartao.substring(numeroCartao.length() - 4);
            detalhes = String.format("Cartão: %s (último dígito: %d)", cartaoMascarado, digitoInt);
            mensagem = aprovado
                    ? "Pagamento aprovado - Último dígito do cartão é PAR"
                    : "Pagamento rejeitado - Último dígito do cartão é ÍMPAR";

            System.out.println(String.format(
                    "Validação CARTÃO | Agendamento #%d | %s | Último dígito: %d (%s) | Resultado: %s",
                    agendamentoId, cartaoMascarado, digitoInt,
                    (digitoInt % 2 == 0) ? "PAR" : "ÍMPAR",
                    aprovado ? "APROVADO" : "REJEITADO"
            ));

        } else {
            return createErrorResponse("Tipo de pagamento inválido: " + tipoPagamento);
        }

        String status = aprovado ? "APROVADO" : "REJEITADO";

        // Prepara resposta (sem persistir nada)
        JSONObject response = new JSONObject();
        response.put("success", true);
        response.put("agendamento_id", agendamentoId);
        response.put("paciente_id", pacienteId);
        response.put("tipo_pagamento", tipoPagamento);
        response.put("status", status);
        response.put("aprovado", aprovado);
        response.put("mensagem", mensagem);
        response.put("detalhes", detalhes);

        return response;
    }

    private JSONObject createErrorResponse(String message) {
        JSONObject response = new JSONObject();
        response.put("success", false);
        response.put("error", message);
        return response;
    }

    public static void main(String[] args) {
        System.out.println("═══════════════════════════════════════════════════════");
        System.out.println("    SERVIÇO DE VALIDAÇÃO DE CONVÊNIO E PAGAMENTO");
        System.out.println("═══════════════════════════════════════════════════════");
        System.out.println("    Modo: STATELESS (sem banco de dados)");
        System.out.println("  Lógica de Validação:");
        System.out.println("   • CONVÊNIO: Válido se tamanho do nome for PAR");
        System.out.println("   • CARTÃO: Válido se último dígito for PAR");
        System.out.println("═══════════════════════════════════════════════════════\n");

        ConvenioService service = new ConvenioService();
        service.start();
    }
}