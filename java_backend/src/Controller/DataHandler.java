package controller;

import data.Transaction;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.HexFormat;
import java.util.ArrayList;
import java.util.List;

public class DataHandler {
    
    private static final Path USER_STORE = Path.of(
            System.getProperty("user.dir"), "database", "users.db").normalize();
    private static final Path USER_BACKUP = USER_STORE.resolveSibling("users.hashes.backup.db");
    private static final Path TRANSACTION_STORE = USER_STORE.resolveSibling("transactions.db");

    private DataHandler() {
    }

    public static boolean userExists(String username) throws IOException {
        return findUserIndex(loadUsers(), username) >= 0;
    }

    public static void registerUser(String username, String password) throws IOException {
        List<UserRecord> users = loadUsers();
        int insertionIndex = findInsertionIndex(users, username);
        if (insertionIndex < users.size()
                && users.get(insertionIndex).username().equals(username)) {
            throw new IllegalArgumentException("User already exists");
        }
        users.add(insertionIndex, new UserRecord(username, hashPassword(password)));
        saveUsers(users);
    }

    public static boolean authenticate(String username, String password) throws IOException {
        List<UserRecord> users = loadUsers();
        int userIndex = findUserIndex(users, username);
        return userIndex >= 0 && users.get(userIndex).passwordHash().equals(hashPassword(password));
    }

    public static void recordTransaction(String username, String password,
            Transaction transaction) throws IOException {
        if (!authenticate(username, password)) {
            throw new IllegalArgumentException("Authentication failed");
        }
        validateTransaction(username, transaction);

        Path parent = TRANSACTION_STORE.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        String record = String.join(" : ",
                username,
                transaction.getTimestamp().toString(),
                transaction.getSender(),
                transaction.getReceiver(),
                Double.toString(transaction.getAmount()),
                transaction.getDescription());
        Files.writeString(TRANSACTION_STORE, record + System.lineSeparator(),
                StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    public static List<Transaction> getTransactions(String username, String password)
            throws IOException {
        if (!authenticate(username, password)) {
            throw new IllegalArgumentException("Authentication failed");
        }
        List<Transaction> transactions = new ArrayList<>();
        if (!Files.exists(TRANSACTION_STORE)) {
            return transactions;
        }
        for (String line : Files.readAllLines(TRANSACTION_STORE, StandardCharsets.UTF_8)) {
            if (line.isBlank()) {
                continue;
            }
            String[] record = line.split(" : ", 6);
            if (record.length != 6) {
                throw new IOException("Invalid transaction record in " + TRANSACTION_STORE);
            }
            if (!record[0].equals(username)) {
                continue;
            }
            try {
                transactions.add(new Transaction(record[2], record[3],
                        Double.parseDouble(record[4]), Instant.parse(record[1]), record[5]));
            } catch (RuntimeException error) {
                throw new IOException("Invalid transaction record in " + TRANSACTION_STORE, error);
            }
        }
        return transactions;
    }

    private static void validateTransaction(String username, Transaction transaction) {
        if (!Double.isFinite(transaction.getAmount()) || transaction.getAmount() <= 0) {
            throw new IllegalArgumentException("Transaction amount must be greater than zero");
        }
        validateField(username, "username");
        validateField(transaction.getSender(), "sender");
        validateField(transaction.getReceiver(), "receiver");
        validateField(transaction.getDescription(), "description");
    }

    private static void validateField(String value, String field) {
        if (value == null || value.isBlank() || value.contains(" : ")
                || value.contains("|") || value.contains("\r") || value.contains("\n")) {
            throw new IllegalArgumentException("Invalid transaction " + field);
        }
    }

    private static List<UserRecord> loadUsers() throws IOException {
        List<UserRecord> users = new ArrayList<>();
        if (!Files.exists(USER_STORE)) {
            return users;
        }

        String previousUsername = null;
        for (String line : Files.readAllLines(USER_STORE, StandardCharsets.UTF_8)) {
            if (line.isBlank()) {
                continue;
            }
            String[] record = line.split(" : ", 2);
            if (record.length != 2 || record[0].isBlank() || record[1].isBlank()) {
                throw new IOException("Invalid user record in " + USER_STORE);
            }
            if (previousUsername != null && previousUsername.compareTo(record[0]) >= 0) {
                throw new IOException("User store is not in lexicographic order");
            }
            users.add(new UserRecord(record[0], record[1]));
            previousUsername = record[0];
        }
        return users;
    }

    private static void saveUsers(List<UserRecord> users) throws IOException {
        Path parent = USER_STORE.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }

        Path storeTemp = Files.createTempFile(parent, "users-", ".tmp");
        Path backupTemp = Files.createTempFile(parent, "users-hashes-", ".tmp");
        try (BufferedWriter storeWriter = Files.newBufferedWriter(
                storeTemp, StandardCharsets.UTF_8, StandardOpenOption.TRUNCATE_EXISTING);
             BufferedWriter backupWriter = Files.newBufferedWriter(
                     backupTemp, StandardCharsets.UTF_8, StandardOpenOption.TRUNCATE_EXISTING)) {
            for (UserRecord user : users) {
                String record = user.username() + " : " + user.passwordHash();
                storeWriter.write(record);
                storeWriter.newLine();
                backupWriter.write(record);
                backupWriter.newLine();
            }
        }
        moveIntoPlace(storeTemp, USER_STORE);
        moveIntoPlace(backupTemp, USER_BACKUP);
    }

    private static void moveIntoPlace(Path source, Path target) throws IOException {
        try {
            Files.move(source, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } catch (java.nio.file.AtomicMoveNotSupportedException error) {
            Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static int findUserIndex(List<UserRecord> users, String username) {
        int low = 0;
        int high = users.size() - 1;
        while (low <= high) {
            int middle = low + (high - low) / 2;
            int comparison = users.get(middle).username().compareTo(username);
            if (comparison == 0) {
                return middle;
            }
            if (comparison < 0) {
                low = middle + 1;
            } else {
                high = middle - 1;
            }
        }
        return -1;
    }

    private static int findInsertionIndex(List<UserRecord> users, String username) {
        int low = 0;
        int high = users.size();
        while (low < high) {
            int middle = low + (high - low) / 2;
            if (users.get(middle).username().compareTo(username) < 0) {
                low = middle + 1;
            } else {
                high = middle;
            }
        }
        return low;
    }

    private static String hashPassword(String password) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(password.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException error) {
            throw new IllegalStateException("SHA-256 is unavailable", error);
        }
    }

    private record UserRecord(String username, String passwordHash) {
    }
}
