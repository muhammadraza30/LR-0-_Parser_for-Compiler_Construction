int x;
bool flag;
string message;

x = 42;
flag = true;
message = "Hello, World!";

agar (x > 0) {
    dikhao("Positive");
} varna agar (x < 0) {
    dikhao("Non-positive");
}varna {
    dikhao("ZERO");
}

jabtak (x > 0) {
    x = x - 1;
}

tabtak (int i = 0; i < 10; i = i + 1) {
    agar (i % 2 == 0) {
        dikhao("Even: ", i);
    }
}