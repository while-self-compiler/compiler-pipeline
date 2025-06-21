CodeMirror.defineMode("while", function () {
  const keywords = /^(while|do|end|echo)\b/;
  const operators = /^[+\->]/;
  const variable = /^x\d+\b/;
  const number = /^\d+/;

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

      // Numbers
      if (stream.match(number)) {
        return "number";
      }

      if (stream.match("/*")) {
        state.inBlockComment = true;
        return "comment";
      }

      // Line comment (only one slash)
      if (stream.match(/\/(?![*\/])/)) {
        stream.skipToEnd();
        return "comment";
      }

      // Whitespace
      if (stream.eatSpace()) return null;

      // Operators
      if (stream.match(operators)) {
        return "operator";
      }

      // Variables: x followed by digits
      if (stream.match(variable)) {
        return "variable-2";
      }

      // Keywords
      if (stream.match(keywords)) {
        return "keyword";
      }

      // Default case: skip one character
      stream.next();
      return null;
    }
  };
});

CodeMirror.defineMIME("text/x-while", "while");
