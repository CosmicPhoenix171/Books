// Scroll progress bar
window.addEventListener('scroll', function() {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  const scrollProgress = (scrollTop / scrollHeight) * 100;
  const bar = document.getElementById('progress-bar');
  if (bar) {
    bar.style.width = scrollProgress + '%';
  }
});

// Audio player functionality with Web Speech API
if ('speechSynthesis' in window) {
  const playBtn = document.getElementById('play-audio');
  const pauseBtn = document.getElementById('pause-audio');
  const stopBtn = document.getElementById('stop-audio');
  const speedSelect = document.getElementById('audio-speed');
  const voiceSelect = document.getElementById('voice-select');
  
  let utterance = null;
  let isPaused = false;

  // Load available voices
  function loadVoices() {
    const voices = speechSynthesis.getVoices();
    voiceSelect.innerHTML = '';
    voices.forEach((voice, index) => {
      const option = document.createElement('option');
      option.value = index;
      option.textContent = `${voice.name} (${voice.lang})`;
      if (voice.default) {
        option.selected = true;
      }
      voiceSelect.appendChild(option);
    });
  }

  // Load voices on page load and when they change
  loadVoices();
  if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
  }

  if (playBtn) {
    playBtn.addEventListener('click', function() {
      const chapterContent = document.querySelector('.chapter-content');
      if (!chapterContent) return;

      // If paused, resume
      if (isPaused) {
        speechSynthesis.resume();
        isPaused = false;
        playBtn.disabled = true;
        pauseBtn.disabled = false;
        return;
      }

      // If already speaking, do nothing
      if (speechSynthesis.speaking && !isPaused) {
        return;
      }

      const text = chapterContent.innerText || chapterContent.textContent;
      utterance = new SpeechSynthesisUtterance(text);
      
      // Set voice
      const voices = speechSynthesis.getVoices();
      const selectedVoiceIndex = voiceSelect.value;
      if (voices[selectedVoiceIndex]) {
        utterance.voice = voices[selectedVoiceIndex];
      }

      // Set speed
      utterance.rate = parseFloat(speedSelect.value);

      utterance.onend = function() {
        playBtn.disabled = false;
        pauseBtn.disabled = true;
        stopBtn.disabled = true;
      };

      utterance.onerror = function(event) {
        console.error('Speech synthesis error:', event);
        playBtn.disabled = false;
        pauseBtn.disabled = true;
        stopBtn.disabled = true;
      };

      speechSynthesis.speak(utterance);
      playBtn.disabled = true;
      pauseBtn.disabled = false;
      stopBtn.disabled = false;
    });
  }

  if (pauseBtn) {
    pauseBtn.addEventListener('click', function() {
      if (speechSynthesis.speaking && !isPaused) {
        speechSynthesis.pause();
        isPaused = true;
        playBtn.disabled = false;
        pauseBtn.disabled = true;
      }
    });
  }

  if (stopBtn) {
    stopBtn.addEventListener('click', function() {
      speechSynthesis.cancel();
      isPaused = false;
      playBtn.disabled = false;
      pauseBtn.disabled = true;
      stopBtn.disabled = true;
    });
  }

  if (speedSelect) {
    speedSelect.addEventListener('change', function() {
      if (utterance) {
        utterance.rate = parseFloat(speedSelect.value);
      }
    });
  }
}
