#include <iostream>
using namespace std;

int main()
{
    unsigned int n; // define a variable
    unsigned long long factorial = 1; // define a variable and set it equal to 1

    cout << "Enter a positive integer: "; // print something
    cin >> n;

    // loop from 1 to n and multiply the previous result by i
    for(int i = 1; i <=n; ++i)
    {
        factorial *= i;
        /*
        factorial += i; // this doesn't work
        factorial -= i; // this doesn't work either
        */
    }

    cout << "Factorial of " << n << " = " << factorial; // print the result
    return 0;
}
