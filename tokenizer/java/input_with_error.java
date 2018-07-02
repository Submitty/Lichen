public class FunctionCall {
	// this is a comment
    public static void funct1 () {
	System.out.println ("Inside funct1");
    }

    public static void main (String[] args {
	int val;
	System.out.println ("funct2 returned a value of " + val);

	val = funct2(-3);
    public static int funct2 (int param) {
	System.out.println ("Inside funct2 with param " + param);
	return param * 2;
    }
}