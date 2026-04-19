import Editor from "@monaco-editor/react";

export default function MonacoWorkspace({ code, onCodeChange }) {
  return (
    <div className="editor-shell">
      <Editor
        height="58vh"
        language="python"
        theme="vs-dark"
        value={code}
        options={{
          minimap: { enabled: false },
          fontFamily: "JetBrains Mono",
          fontSize: 14,
          scrollBeyondLastLine: false,
          wordWrap: "on",
        }}
        onChange={(value) => onCodeChange(value || "")}
      />
    </div>
  );
}
