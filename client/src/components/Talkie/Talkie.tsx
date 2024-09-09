import React, { useRef, useEffect, useState } from "react";
import "./talkie.css";



interface TalkieProps {
  processAudio: (audioFile: Blob, transcription: string) => void;
}

export const Talkie: React.FC<TalkieProps> = ({ processAudio }) => {
  const [isRecording, setIsRecording] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const transcriptionRef = useRef<string>("");
  const barsContainerRef = useRef<HTMLDivElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const barsRef = useRef<HTMLDivElement[]>([]);
  const animationIdRef = useRef<number | null>(null); // Ref para almacenar el ID de la animación

  const numBars = 30; 

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    const audioContext = new AudioContext();
    audioContextRef.current = audioContext;
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current = analyser;
    dataArrayRef.current = dataArray;

    source.connect(analyser);

    mediaRecorder.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
      }
      processAudio(audioBlob, transcriptionRef.current);
      resetState(); // Reiniciar todo al detener la grabación
    };

    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const resetState = () => {
    // Reiniciar las barras
    barsRef.current.forEach(bar => {
      bar.style.height = "1px";
    });

    // Limpiar los chunks de audio
    audioChunksRef.current = [];

    // Restablecer la transcripción
    transcriptionRef.current = "";

    // Detener la animación
    if (animationIdRef.current !== null) {
      cancelAnimationFrame(animationIdRef.current);
    }
  };

  const animateBars = () => {
    if (!analyserRef.current || !dataArrayRef.current) return;

    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;

    const animate = () => {
      if (!isRecording) {
        return;
      }
      animationIdRef.current = requestAnimationFrame(animate); // Almacenar el ID de la animación

      analyser.getByteFrequencyData(dataArray);

      const step = Math.floor(dataArray.length / numBars);

      for (let i = 0; i < numBars; i++) {
        const barHeight = dataArray[i * step] / 2;

        if (barsRef.current[i]) {
          barsRef.current[i].style.height = `${barHeight}px`;
        }
      }
    };

    animate();
  };

  useEffect(() => {
    if (barsContainerRef.current) {
      for (let i = 0; i < numBars; i++) {
        const bar = document.createElement("div");
        bar.classList.add("bar");
        barsContainerRef.current.appendChild(bar);
        barsRef.current.push(bar);
      }
    }
  }, []);

  useEffect(() => {
    if (isRecording) {
      animateBars();
      // @ts-ignore
      const recognition = new (window.SpeechRecognition ||
        (window as any).webkitSpeechRecognition)();
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        let interimTranscription = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            transcriptionRef.current += transcript;
          } else {
            interimTranscription += transcript;
          }
        }
        console.log(
          "Transcription: ",
          transcriptionRef.current + interimTranscription
        );
      };

      recognition.start();

      return () => {
        recognition.stop();
        if (animationIdRef.current !== null) {
          cancelAnimationFrame(animationIdRef.current);
        }
      };
    }
  }, [isRecording]);

  return (
    <div className="talkie">
      <div id="bars-container" ref={barsContainerRef}></div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? "Stop Recording" : "Start Recording"}
      </button>
    </div>
  );
};
