"use client";
import { useState, useRef, useEffect } from "react";
import styles from "./page.module.css";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";


export default function Home() {
  const [input, setInput] = useState("");
  // const [apiKey, setApiKey] = useState(""); // We'll manage API keys in the backend
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // State for file upload menu - temporarily disabled
  // const [fileMenuOpen, setFileMenuOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // const [uploadedFileName, setUploadedFileName] = useState<string>("");
  // Upload status for feedback - temporarily disabled
  // const [uploadStatus, setUploadStatus] = useState<string>("");
  // Track if a PDF has been uploaded successfully - temporarily disabled
  // const [pdfUploaded, setPdfUploaded] = useState<boolean>(false);

  // Scroll to bottom on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Handle sending a message
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!input.trim()) {
      setError("Please fill in all fields before submitting.");
      return;
    }
    const newMessages = [
      ...messages,
      { role: "user", content: input }
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    try {
      // API URL now points to our new backend invoke endpoint
      const apiUrl = "http://localhost:8000/invoke";

      // The request body is simplified to match the backend schema
      const requestBody = {
        input: input,
      };

      const res = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!res.ok || !res.body) {
        const errorMsg = `API error: ${res.status}`;
        let errorDetail = "";
        try {
          const data = await res.json();
          if (data && data.detail) {
            if (typeof data.detail === "string") {
              errorDetail = data.detail;
            } else if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
              errorDetail = data.detail[0].msg;
            }
          }
        } catch { }
        switch (res.status) {
          case 400:
            setError("Invalid request. Please check your input and try again.\nInstruction: Ensure all fields are filled and valid.");
            break;
          case 401:
          case 403:
            setError("Error: Authorization failed.\nInstruction: Please check your backend configuration. You may be missing an API key.");
            break;
          case 404:
            setError("Requested resource or model not found.\nInstruction: Please check the model name or contact support if the issue persists.");
            break;
          case 422:
            setError(`Missing or invalid input.\nInstruction: ${errorDetail || "Please fill in all required fields correctly."}`);
            break;
          case 500:
            setError("Server error.\nInstruction: The server is currently unavailable. Please try again later or contact support if the issue persists.");
            break;
          default:
            setError(`Error: ${errorMsg}${errorDetail ? `\nDetails: ${errorDetail}` : ""}\nInstruction: An unexpected error occurred. Please try again or contact support.`);
        }
        setLoading(false);
        return;
      }

      // Stream the response from our backend
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let buffer = "";

      setMessages(msgs => [
        ...msgs,
        { role: "assistant", content: "" }
      ]);

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          buffer += decoder.decode(value, { stream: true });
          console.log("buffer:", buffer);

          // Extract all content from the buffer, ignoring SSE formatting
          const allContent = buffer.replace(/data: /g, '').replace(/\n\n/g, '\n').trim();

          if (allContent && allContent !== '[DONE]') {
            console.log("Extracted content from buffer:", allContent);
            console.log("Content length:", allContent.length);

            setMessages(msgs => {
              const newMessages = [...msgs];
              const lastMessageIndex = newMessages.length - 1;

              // Replace the assistant's message content with the complete response
              if (lastMessageIndex >= 0 && newMessages[lastMessageIndex].role === "assistant") {
                newMessages[lastMessageIndex] = {
                  ...newMessages[lastMessageIndex],
                  content: allContent,  // REPLACE instead of append
                };
                console.log("Updated message content length:", newMessages[lastMessageIndex].content.length);
              }
              return newMessages;
            });
          }

          // Clear the buffer after processing
          buffer = "";
        }

      }
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string' && err.message.toLowerCase().includes("network")) {
        setError("Error: Network error.\nInstruction: Could not connect to the backend. Please ensure it is running and accessible.");
      } else {
        setError(`Error: ${err instanceof Error ? err.message : String(err)}\nInstruction: An unexpected error occurred. Please try again or contact support.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) {
        // Manually trigger form submission
        (e.target as HTMLTextAreaElement).form?.requestSubmit();
      }
    }
  };

  function convertLatexDelimiters(text: string): string {
    // Convert \[ ... \] to $$ ... $$
    text = text.replace(/\\\[((?:.|\n)*?)\\\]/g, (_, expr) => `$$${expr}$$`);
    // Convert [ ... ] to $$ ... $$
    text = text.replace(/\\[((?:.|\n)*?)\\]/g, (_, expr) => `$$${expr}$$`);
    // Convert \( ... \) to $ ... $
    text = text.replace(/\\\(((?:.|\n)*?)\\\)/g, (_, expr) => `$${expr}$`);
    // Convert ( ... ) to $ ... $
    text = text.replace(/\\(((?:.|\n)*?)\\)/g, (_, expr) => `$${expr}$`);
    return text;
  }

  // Handle PDF upload - currently disabled but kept for future implementation
  // const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
  //   if (e.target.files && e.target.files.length > 0) {
  //     const file = e.target.files[0];
  //     setUploadedFileName(file.name);
  //     setUploadStatus("Uploading...");
  //     // setFileMenuOpen(false);
  //     try {
  //       const isPdf = file.type === "application/pdf";
  //       const isImage = [
  //         "image/png",
  //         "image/jpeg",
  //         "image/heif",
  //         "image/heic"
  //       ].includes(file.type);
  //       if (!isPdf && !isImage) {
  //         setUploadStatus("Only PNG, JPEG, HEIF, HEIC images or PDF files are supported.");
  //         return;
  //       }
  //       const apiUrl = isPdf
  //         ? (typeof window !== "undefined" && window.location.hostname === "localhost"
  //           ? "http://localhost:8000/api/upload-pdf"
  //           : "/api/upload-pdf")
  //         : (typeof window !== "undefined" && window.location.hostname === "localhost"
  //           ? "http://localhost:8000/api/upload-file"
  //           : "/api/upload-file");
  //       const formData = new FormData();
  //       formData.append("file", file);
  //       // if (isPdf) {
  //       //   formData.append("api_key", apiKey);
  //       // }
  //       const res = await fetch(apiUrl, {
  //         method: "POST",
  //         body: formData,
  //       });
  //       if (!res.ok) {
  //         const data = await res.json().catch(() => ({}));
  //         let detail = data.detail;
  //         if (Array.isArray(detail)) {
  //           detail = detail.map(d => d.msg || JSON.stringify(d)).join(' | ');
  //         } else if (detail && typeof detail === "object") {
  //           detail = detail.msg || JSON.stringify(detail, null, 2);
  //         }
  //         setUploadStatus(detail || `Upload failed: ${res.status}`);
  //         return;
  //       }
  //       const data = await res.json();
  //       setUploadStatus(`File uploaded!${isPdf && data.chunks_indexed ? ` Chunks: ${data.chunks_indexed}` : ""}`);
  //       if (isPdf && data.chunks_indexed) {
  //         // setPdfUploaded(true);
  //       }
  //     } catch (err) {
  //       setUploadStatus(`Upload error: ${err instanceof Error ? err.message : String(err)}`);
  //     }
  //   }
  // };

  // Debug: Log fileInputRef after every render
  useEffect(() => {
    console.log('fileInputRef.current after render:', fileInputRef.current);
  });

  // Handler for clicking outside the menu to close it - temporarily disabled
  // useEffect(() => {
  //   if (!fileMenuOpen) return;
  //   function handleClick() {
  //     setFileMenuOpen(false);
  //   }
  //   document.addEventListener("mousedown", handleClick);
  //   return () => document.removeEventListener("mousedown", handleClick);
  // }, [fileMenuOpen]);

  return (
    <div className={styles.page}>
      {/* Sidebar for system prompt */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <span className={styles.sidebarText}>🏠</span>
          <span className={styles.sidebarTitle}>Advocate</span>
        </div>
        {/* API Key input is removed from the UI */}
        {/* <div className={styles.apiKeyContainer}>
          <label className={styles.label}>OpenAI API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            className={styles.apiKeyInput}
            required
          />
        </div> */}
        <button
          onClick={() => {
            setMessages([]);
            setInput("");
            setError("");
            setLoading(false);
            // setPdfUploaded(false);
            // setUploadedFileName("");
            // setUploadStatus("");
          }}
          className={styles.clearButton}
        >
          Clear Chat
        </button>
      </aside>

      {/* Main chat area */}
      <main className={styles.mainContent}>
        <div className={styles.chatContainer}>
          {messages.map((m, i) => {
            const content = convertLatexDelimiters(m.content);
            if (m.role === "assistant") {
              console.log("Rendering assistant message:", content);
            }
            return (
              <div key={i} className={`${styles.message} ${m.role === 'user' ? styles.user : styles.assistant}`}>
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {content}
                </ReactMarkdown>
              </div>
            );
          })}
          {loading && (
            <div className={`${styles.message} ${styles.assistant}`}>
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {convertLatexDelimiters("Thinking...")}
              </ReactMarkdown>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form} style={{ position: 'relative' }}>
          {/* File upload (+) button is temporarily disabled */}
          {/* <div className={styles.plusMenuWrapper}>
            <button
              type="button"
              className={styles.plusButton}
              aria-label="Add options"
              onClick={e => {
                e.stopPropagation();
                if (fileInputRef.current) {
                  fileInputRef.current.click();
                }
              }}
            >
              +
            </button>
            <input
              id="file-upload-debug"
              type="file"
              accept=".png,.jpeg,.jpg,.heif,.heic,application/pdf,image/png,image/jpeg,image/heif,image/heic"
              ref={fileInputRef}
              style={{ display: 'none' }}
              // onChange={handleFileInputChange}
            />
          </div> */}
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Welcome to ManualAIze! I am here to help you find the answers you need. Ask me anything..."
            className={styles.textarea}
            rows={5}
            style={{ maxHeight: '120px', minHeight: '40px', overflowY: 'auto' }}
          />
          <button type="submit" disabled={loading} className={styles.button}>
            {loading ? "..." : "Send"}
          </button>
        </form>
        {/* Show uploaded file name if any - temporarily disabled */}
        {/* {(uploadedFileName || uploadStatus) && (
          <div className={styles.uploadedFileName}>
            {uploadedFileName && `Selected: ${uploadedFileName}`}<br />
            {uploadStatus && uploadStatus}
          </div>
        )} */}
      </main>
    </div>
  );
}