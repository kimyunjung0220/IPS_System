/*
const addBtn = document.getElementById('addBtn');
const itemInput = document.getElementById('itemInput');
const itemList = document.getElementById('itemList');

// 아이템 추가 함수
function addItem() {
  const value = itemInput.value.trim();
  if (value === '') {
    alert('규칙을 입력하세요!');
    return;
  }

  const li = document.createElement('li');
  li.textContent = value;
  

  const delBtn = document.createElement('button');
  delBtn.textContent = '삭제';
  delBtn.className = 'deleteBtn';
  delBtn.onclick = function() {
    itemList.removeChild(li);
  };

  li.appendChild(delBtn);
  itemList.appendChild(li);
  itemInput.value = '';
  itemInput.focus();
}

// 추가 버튼 클릭 이벤트
addBtn.addEventListener('click', addItem);

// 엔터키로도 추가 가능하게
itemInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    addItem();
  }
}); */

const socketac = io("/send_rule");

socketac.on('connect', () => {
  socketac.emit('request_data');
});

socketac.on('rule_list', (msg) =>{
  const itemInput = document.getElementById('itemInput');
  const itemList = document.getElementById('itemList');

  const li = document.createElement('li');
  li.textContent = msg.data;

  const delbtn = document.createElement('button');
  delbtn.textContent = '삭제';
  delbtn.className = 'deleteBtn';

    delbtn.addEventListener('click', () => {
        const formData = new FormData(); 
        formData.append("flag", "del_rule");
        formData.append("rule" , msg.data);
        fetch('/rule', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        }).then(() => {
            window.location.href = "/rule";
        });
    });

  li.appendChild(delbtn);
  itemList.appendChild(li);
  itemInput.value = '';
  itemInput.focus();
})
