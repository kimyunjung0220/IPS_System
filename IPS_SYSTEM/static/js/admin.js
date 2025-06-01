const socketac = io("/send_account");

socketac.on('connect', () => {
    socketac.emit('request_data');
});

socketac.on('user_account', (msg) => {
    const userid = msg.data["userid"];
    const name = msg.data['name'];
    const permit = msg.data['permit'];

    const dataElments = document.getElementById("account_list");
    const newtr = document.createElement('tr');

    const divname = document.createElement('td');
    const divid = document.createElement('td');
    const divpermit = document.createElement('td');
    const delbtn = document.createElement('button');

    divid.textContent = userid;
    divname.textContent = name;
    divpermit.textContent = permit;

    delbtn.textContent = "삭제";
    delbtn.id = "del_member_btn";

    delbtn.addEventListener('click', () => {
        const formData = new FormData();  // 여기서 새로 생성!
        formData.append("flag", "del_member");
        formData.append("account", `${name}:${userid}`);
        formData.append("permit", permit);

        fetch('/admin_pages', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        }).then(() => {
            window.location.href = "/admin_pages";
        });
    });

    newtr.append(divname, divid, divpermit, delbtn);
    dataElments.appendChild(newtr);
});


const socketip = io("/send_whitelist");

socketip.on('connect', () => {
    socketip.emit('request_data');
});

socketip.on('white_list', (msg) => {
    const ip = msg.data;

    const dataElments = document.getElementById("white_list");
    const newtr = document.createElement('tr');
    const divip = document.createElement('td');
    const delbtn = document.createElement('button');

    divip.textContent = ip;
    divip.style.width = "37vw";
    delbtn.textContent = "삭제";
    delbtn.id ="del_ip_btn";

    delbtn.addEventListener('click', () => {
        const formData = new FormData();  // 여기서 새로 생성!
        formData.append("flag", "del_ip");
        formData.append("ip", ip);

        fetch('/admin_pages', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        }).then(() => {
            window.location.href = "/admin_pages";
        });
    });

    newtr.append(divip, delbtn);
    dataElments.appendChild(newtr);
});
