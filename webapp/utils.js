/**
 * Converts text to uppercase and returns the ASCII representation as a BigInt
 * @param {string} text - The input text to convert
 * @returns {bigint} - The ASCII representation as a BigInt
 */
function textToAsciiBigInt(text) {
  // Use the helper function to get the hex string
  const hexString = textToAsciiHex(text);
  
  // Convert the concatenated hex string to a BigInt
  return BigInt("0x" + hexString);
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
