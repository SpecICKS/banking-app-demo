package Controller;

import Read.Key;

public class Controller {

    public static void main(String[] args) {
        Key data = new Key();
        if(args.length == 0) {
            System.err.println("Error at credentials path, no argument passed");
            System.exit(2);
        }
        if (!data.readData(args[0])) {
            System.exit(1);
        }
        if (data.type.equals("REGISTER")) {
            //code for registering
        } else {
            //code for login
        }
    }
}
