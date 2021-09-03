import sys
hex_str = ''.join([chr(i) if len(repr(chr(i))) == 3 else '.' for i in range(256)])

def hexdump(string):
    off_by = len(string)%16
    count = 0
    while True:
        word = string[count:count+16]
        count += 16
        printable  = word.translate(bytes(hex_str,'utf-8'))
        hex_word = ''.join([f'{ord(c):02X} ' for c in word])
        print(f' {hex_word}\t|{printable}')
        if len(string) - count == off_by:
            break

    word = string[count:count+off_by]
    hex_word = ''.join(f'{ord(c):02X} ' for c in word)
    printable = word.translate(hex_str)
    spaces = ''.join(['\x20\x20\x20' for i in range(16-off_by)])
    print(f' {hex_word} {spaces}\t|{printable}')

if __name__ == '__main__':
    if(len(sys.argv) == 2):
        to_dump = sys.argv[1]
    else:
        to_dump = sys.stdin.read()

    hexdump(to_dump)
