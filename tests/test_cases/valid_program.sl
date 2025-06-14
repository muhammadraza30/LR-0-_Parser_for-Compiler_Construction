
int x;
bool flag;
string message;

x = 42;
flag = true;
message = "Hello, World!";

if (x > 0) {
    dikhao("Positive");
} else if (x < 0) {
    dikhao("Non-positive");
}else {
    dikhao("ZERO");
}

while (x > 0) {
    x = x - 1;
}

for (int i = 0; i < 10; i = i + 1) {
    if (i % 2 == 0) {
        dikhao("Even: ", i);
    }
}