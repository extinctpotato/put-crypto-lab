# Declare a string.
text_str = "Hello, world!"

# Encode to ASCII byte array.
text_bytes = text_str.encode(encoding='ascii')

# Interpret as integer, byte order is little endian.
text_int = int.from_bytes(msg.encode(), 'LITTLE')
