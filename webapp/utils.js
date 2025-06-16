/**
 * Converts text to uppercase and returns the ASCII representation as a BigInt
 * @param {string} text - The input text to convert
 * @returns {object} - Object with bigint and byteCount properties
 */
function textToAsciiBigInt(text) {
  // Use the helper function to get the hex string
  const hexString = textToAsciiHex(text);
  
  // Convert text to uppercase to get the byte count
  const uppercaseText = text.toUpperCase();
  const byteCount = uppercaseText.length;
  
  // Convert the concatenated hex string to a BigInt
  const bigint = BigInt("0x" + hexString);
  
  return {
    bigint: bigint,
    byteCount: byteCount
  };
}

/**
 * Helper function to get the hex string representation (for display purposes)
 * @param {string} text - The input text to convert
 * @returns {string} - The hex string representation
 */
function textToAsciiHex(text) {
  const uppercaseText = text.toUpperCase();
  let hexString = "";
  for (let i = 0; i < uppercaseText.length; i++) {
    const ascii = uppercaseText.charCodeAt(i);
    const hex = ascii.toString(16).padStart(2, '0');
    hexString += hex;
  }
  return hexString;
}
