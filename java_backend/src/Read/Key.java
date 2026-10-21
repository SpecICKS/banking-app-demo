package read;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class Key {
    public String username = "";
    public String password = "";
    public String type = "";
    public String sender = "";
    public String receiver = "";
    public String amount = "";
    public String description = "";

    public boolean readData(String path) {
        try (Scanner scan = new Scanner(new File(path), StandardCharsets.UTF_8)) {
            if (!scan.hasNextLine()) {
                throw new IllegalArgumentException("Missing action");
            }
            type = scan.nextLine();
            if (!scan.hasNextLine()) {
                throw new IllegalArgumentException("Missing username");
            }
            username = scan.nextLine();
            if (!scan.hasNextLine()) {
                throw new IllegalArgumentException("Missing password");
            }
            password = scan.nextLine();
            if (type.equals("RECORD_TRANSACTION")) {
                sender = readRequired(scan, "sender");
                receiver = readRequired(scan, "receiver");
                amount = readRequired(scan, "amount");
                description = readRequired(scan, "description");
            }
            System.out.println("Credential request parsed successfully.");
            return true;
        } catch (IOException | IllegalArgumentException e) {
            System.err.println("Credential request parsing failed: " + e.getMessage());
            return false;
        }
    }

    private static String readRequired(Scanner scan, String field) {
        if (!scan.hasNextLine()) {
            throw new IllegalArgumentException("Missing " + field);
        }
        return scan.nextLine();
    }
}
