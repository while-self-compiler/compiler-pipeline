CodeMirror.defineMode("ewhile", function () {
  const keywords = /^(let|macro|use|while|if|do|then|end|else|echo)\b/i;
  const operators = /^[=+\-*/<>%]/;
  const identifier = /^[a-zA-Z][a-zA-Z0-9_]*/;
  const number = /^\d+/;
  const specialVar = /^[xX]\d+\b/;

  return {
    startState: function () {
      return { inBlockComment: false };
    },
    token: function (stream, state) {
      // Block comment
      if (state.inBlockComment) {
        if (stream.skipTo("*/")) {
          stream.next(); stream.next(); // skip past */
          state.inBlockComment = false;
        } else {
          stream.skipToEnd();
        }
        return "comment";
      }

      if (stream.match("/*")) {
        state.inBlockComment = true;
        return "comment";
      }

      // Line comment
      if (stream.match("//") || stream.match(/\/(?!\/|\*)/)) {
        stream.skipToEnd();
        return "comment";
      }

      // Whitespace
      if (stream.eatSpace()) return null;

      // Operators
      if (stream.match(operators)) {
        return "operator";
      }

      // Numbers
      if (stream.match(number)) {
        return "number";
      }

      // Special X variables
      if (stream.match(specialVar)) {
        return "string"; // could also be "atom" or other custom style
      }

      // Keywords
      if (stream.match(keywords)) {
        return "keyword";
      }

      // macro/use with name
      if (stream.match(/^(macro|use)\s+([a-zA-Z][a-zA-Z0-9_]*)/, false)) {
        stream.match(/^(macro|use)/);
        return "keyword";
      }

      // Identifiers
      if (stream.match(identifier)) {
        return "variable";
      }

      // Default: move ahead one character
      stream.next();
      return null;
    }
  };
});

CodeMirror.defineMIME("text/x-ewhile", "ewhile");
