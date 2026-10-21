package data;

import java.time.Instant;

public class Transaction {
    private final String sender;
    private final String receiver;
    private final double amount;
    private final Instant timestamp;
    private final String description;

    public Transaction(String sender, String receiver, double amount) {
        this(sender, receiver, amount, Instant.now(), "");
    }

    public Transaction(String sender, String receiver, double amount,
            Instant timestamp, String description) {
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
        this.timestamp = timestamp;
        this.description = description;
    }

    public String getSender() {
        return sender;
    }

    public String getReceiver() {
        return receiver;
    }

    public double getAmount() {
        return amount;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public String getDescription() {
        return description;
    }
}
