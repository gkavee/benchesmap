import config from '../../config';
import React, { useState } from 'react';
import Button from '@mui/material/Button';
import Modal from '@mui/material/Modal';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import ReactDOM from 'react-dom';

const LinkTelegram = () => {
  const [tgUsername, setTgUsername] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async () => {
    const baseUrl = `${config.apiUrl}/link_tg`;
    const params = new URLSearchParams({ tg_username: tgUsername });
    const url = `${baseUrl}?${params}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Request failed with status ' + response.status);
        }

        setResponseMessage(`@${tgUsername} привязан к вашему аккаунту`);

        const responseData = await response.json();
        console.log('Response from server:', responseData);
    } catch (error) {
        console.error('Error while sending POST request:', error);
        setResponseMessage('Произошла ошибка: ' + error.message);
    }
};

  return ReactDOM.createPortal(
    <div>
      <Button onClick={() => setShowModal(true)} style={{ zIndex: 2, marginTop: '66px' }}>Link TG</Button>
      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 300,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: '3px'
          }}
        >
          <p id="modal-modal-description">
          <TextField
            sx={{ width: '100%' }}
            id="outlined-basic"
            label="username"
            variant="outlined"
            value={tgUsername}
            onChange={(e) => {
              const value = e.target.value.replace(/[^a-zA-Z0-9_]/g, '');
              setTgUsername(value);
            }}
            inputProps={{ maxLength: 32 }}
          />
          </p>
          <Button variant="contained" onClick={handleSubmit} sx={{ marginLeft: '180px' }}>Отправить</Button>
          <p>{responseMessage}</p>
        </Box>
      </Modal>
    </div>,
    document.body
  );
};

export default LinkTelegram;