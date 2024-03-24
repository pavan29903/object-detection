import React, { useState, useRef } from 'react';
import axios from 'axios';

export function ObjectDetection() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [images, setImages] = useState([]);
    const [detectionResults, setDetectionResults] = useState([]);

    const inputRef = useRef(null);

    const inputChange = () => {
        inputRef.current.click();
    }

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleSubmit = async () => {
        if (!selectedFile) {
            alert('Please select an image');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
        
            const response = await axios.post('http://localhost:5009/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

    
            const newImage = {
                uploadedImage: `data:image/jpeg;base64,${response.data.uploaded_image}`,
                renderedImage: `data:image/jpeg;base64,${response.data.rendered_image}`
            };
            const newDetectionResults = response.data.detection_results || {}; 
            setDetectionResults([newDetectionResults, ...detectionResults]);
            setImages([newImage, ...images]);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div className=''>
            <div className=''>
                <div className='flex justify-center flex-col items-center '>
                    <h1 className=' font-semibold text-[42px]'>Object Detection</h1>
                    <h3 className='p-5 text-[#47474f]'>Detect the objects in your image</h3>
        
                    <button className="bg-[#3b82f6] w-[330px] h-[80px] rounded-xl " onClick={inputChange}>Upload Image</button>
                    <input type="file" ref={inputRef} onChange={handleFileChange} accept="image/*" className='invisible' />

                    <button className='bg-green-400 w-[100px] h-[60px] rounded-xl' onClick={handleSubmit}>Verify Image</button>
                </div>
                <div className='inline-block p-10'>
                    {images.map((image, index) => (
                        <div key={index} className='inline-block p-10 md:flex justify-center'>
                            <div className='flex flex-col p-10'>
                                <h2 className='flex justify-center font-medium font-serif text-[30px] py-10 whitespace-nowrap'>Uploaded image</h2>
                                <img className='rounded-xl' src={image.uploadedImage} alt="hello" />
                            </div>
                            <div className='flex flex-col p-10'>
                                <h2 className='flex justify-center font-medium font-serif text-[30px] py-10 whitespace-nowrap'>Object Detection Result</h2>
                                <img className='rounded-xl' src={image.renderedImage} alt="jslkd" />
                                {detectionResults[index] && (
                                    <div className='p-5'>
                                        <h2 className='font-semibold text-lg'>Detection Results</h2>
                                        <p>Cars: {detectionResults[index].cars}</p>
                                        <p>Buses: {detectionResults[index].buses}</p>
                                        <p>Motorbikes: {detectionResults[index].motorbikes}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
