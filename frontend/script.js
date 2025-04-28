// frontend/script.js

// Global variable to store the suggested code for integration
let currentSuggestedCode = "";

async function getSuggestion() {
    const selectedCode = document.getElementById('selectedCode').value;
    const userPrompt = document.getElementById('userPrompt').value;
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const errorDetailsP = document.getElementById('errorDetails');
    const suggestButton = document.getElementById('suggestButton');
    const integrateButton = document.getElementById('integrateButton');
    const explanationDiv = document.getElementById('explanation');
    const suggestedCodeContainer = document.getElementById('suggestedCode').querySelector('pre code'); // Target the <code> tag


    // Basic validation
    if (!selectedCode.trim() || !userPrompt.trim()) {
        alert("Please provide both the code snippet and a description of the desired change.");
        return;
    }

    // --- UI Update: Start Loading ---
    suggestButton.disabled = true;
    suggestButton.textContent = 'Generating...';
    resultDiv.style.display = 'none'; // Hide previous results
    errorDiv.style.display = 'none'; // Hide previous errors
    loadingDiv.style.display = 'block'; // Show loading indicator
    integrateButton.style.display = 'none'; // Hide integrate button
    currentSuggestedCode = ""; // Clear previous suggestion
    // ---

    try {
        const response = await fetch('http://127.0.0.1:8000/suggest', { // Use 127.0.0.1 instead of localhost sometimes helps
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json', // Explicitly accept JSON
             },
            body: JSON.stringify({
                selected_code: selectedCode,
                user_prompt: userPrompt
            })
        });

        const responseData = await response.json(); // Try to parse JSON regardless of status code for more info

        if (!response.ok) {
             // Use detail from JSON error response if available, otherwise use status text
            const errorMsg = responseData.detail || `HTTP error! Status: ${response.status} ${response.statusText}`;
            throw new Error(errorMsg);
        }

        // --- Process Successful Response ---
        if (responseData.explanation && responseData.suggested_code) {
            explanationDiv.textContent = responseData.explanation; // Use textContent to prevent XSS
            suggestedCodeContainer.textContent = responseData.suggested_code; // Set code content

            // Store suggested code for integration
            currentSuggestedCode = responseData.suggested_code;

             // Apply syntax highlighting with PrismJS
            // Detect language or set a default - you might want more sophisticated detection
            // For now, let's assume Python or let autoloader guess based on content if possible
            suggestedCodeContainer.className = 'language-python'; // Reset class, change 'python' as needed
            Prism.highlightElement(suggestedCodeContainer);

            resultDiv.style.display = 'block'; // Show results section
            integrateButton.style.display = 'inline-block'; // Show integrate button
        } else {
            // Handle cases where the response is ok, but JSON structure is wrong (based on backend fallback)
            if (responseData.explanation && responseData.explanation.startsWith("Error: AI did not return valid JSON")) {
                 throw new Error(responseData.explanation); // Treat as error
            } else {
                 throw new Error("Received an unexpected response format from the server.");
            }
        }
         // ---

    } catch (error) {
        console.error("Error fetching suggestion:", error);
        // --- UI Update: Show Error ---
        errorDetailsP.textContent = error.message || "An unknown error occurred.";
        errorDiv.style.display = 'block'; // Show error message display
         // ---
    } finally {
         // --- UI Update: End Loading ---
        loadingDiv.style.display = 'none'; // Hide loading indicator
        suggestButton.disabled = false; // Re-enable button
        suggestButton.textContent = 'Get Suggestion ✨';
        // ---
    }
}

function integrateCode() {
    const selectedCodeTextarea = document.getElementById('selectedCode');
    if (currentSuggestedCode) {
        selectedCodeTextarea.value = currentSuggestedCode; // Replace original code with suggested code
        // Optionally, provide feedback to the user
        alert("Code integrated into the text area!");

        // Hide the result section or integrate button after integration? Your choice.
        // document.getElementById('result').style.display = 'none';
        // document.getElementById('integrateButton').style.display = 'none';
    } else {
        alert("No suggested code available to integrate.");
    }
}