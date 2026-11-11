package controller;

import java.io.IOException;
import data.Transaction;
import java.util.List;

import read.Key;

public class Controller {

    public static void main(String[] args) {
        Key data = new Key();
        if (args.length != 1) {
            System.err.println("Invalid backend arguments: expected one credentials-file path.");
            System.exit(2);
        }
        boolean debug = Boolean.parseBoolean(System.getProperty("backend.debug", "false"));
        if (!data.readData(args[0], debug)) {
            System.exit(1);
        }
        try {
            if (data.type.equals("REGISTER")) {
                DataHandler.registerUser(data.username, data.password);
                System.out.println("Registration completed successfully.");
            } else if (data.type.equals("LOGIN")) {
                System.out.println("SESSION|" + DataHandler.createSession(
                        data.username, data.password));
            } else if (data.type.equals("RECORD_TRANSACTION")) {
                DataHandler.recordTransaction(data.username, data.password,
                        new Transaction(data.sender, data.receiver,
                                Double.parseDouble(data.amount), java.time.Instant.now(),
                                data.description));
                System.out.println("Transaction recorded successfully.");
            } else if (data.type.equals("GET_TRANSACTIONS")) {
                List<Transaction> transactions = DataHandler.getTransactions(data.username, data.password);
                for (Transaction transaction : transactions) {
                    System.out.println("TRANSACTION|" + transaction.getTimestamp()
                            + "|" + transaction.getSender()
                            + "|" + transaction.getReceiver()
                            + "|" + transaction.getAmount()
                            + "|" + transaction.getDescription());
                }
            } else if (data.type.equals("RECORD_TRANSACTION_SESSION")) {
                DataHandler.recordTransactionWithSession(data.username, data.token,
                        new Transaction(data.sender, data.receiver,
                                Double.parseDouble(data.amount), java.time.Instant.now(),
                                data.description));
            } else if (data.type.equals("GET_TRANSACTIONS_SESSION")) {
                List<Transaction> transactions = DataHandler.getTransactionsWithSession(
                        data.username, data.token);
                for (Transaction transaction : transactions) {
                    System.out.println("TRANSACTION|" + transaction.getTimestamp()
                            + "|" + transaction.getSender()
                            + "|" + transaction.getReceiver()
                            + "|" + transaction.getAmount()
                            + "|" + transaction.getDescription());
                }
            } else if (data.type.equals("LOGOUT_SESSION")) {
                DataHandler.revokeSession(data.username, data.token);
            } else {
                System.err.println("Credential request rejected: unsupported action '" + data.type + "'.");
                System.exit(2);
            }
        } catch (IllegalArgumentException error) {
            System.err.println("Request rejected: " + error.getMessage());
            System.exit(3);
        } catch (IOException | IllegalStateException error) {
            System.err.println("Backend storage failure: " + error.getMessage());
            System.exit(5);
        }
    }

}
