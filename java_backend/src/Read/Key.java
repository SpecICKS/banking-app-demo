package Read;

import java.io.File;
import java.util.Scanner;

public class Key {
    public String username = "";
    public String password = "";
    public void readData(String path) {
        try {
            Scanner scan = new Scanner(new File(path));
            if (scan.hasNextLine()) {
                username = scan.nextLine();
            }
            if (scan.hasNextLine()) {
                password = scan.nextLine();
            }
            scan.close();
            System.out.println("Success Reading!");
        } catch (Exception _) {
            System.out.println("Err: No such file found");
        }
    }
}
