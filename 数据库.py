< !DOCTYPE
html >
< html >
< head >
< meta
charset = "UTF-8" >
< title > 无懈可击报表修改工具（密码保护版） < / title >
< style >
body
{
    font - family: Arial, sans - serif;
max - width: 800
px;
margin: 20
px
auto;
padding: 20
px;
box - shadow: 0
0
10
px
rgba(0, 0, 0, 0.1);
}
.warning
{color: red;}
.input - group
{margin: 15px 0;}
input[type = "file"], input[type = "number"] {
    padding: 8px;
width: 300
px;
}
button
{
    background:  # 007bff;
        color: white;
padding: 10
px
20
px;
border: none;
cursor: pointer;
}
# passwordSection {
margin - bottom: 25
px;
padding: 15
px;
background:  # f5f5f5;
border - radius: 5
px;
}
# passwordStatus {
margin - left: 15
px;
font - weight: bold;
}
< / style >
    < / head >
        < body >
        < div
id = "passwordSection" >
     < h3 > 安全验证 < / h3 >
                         < input
type = "password"
id = "passwordInput"
placeholder = "请输入访问密码"
style = "padding:8px;width:200px;" >
        < button
onclick = "verifyPassword()" > 验证密码 < / button >
                                            < span
id = "passwordStatus" > < / span >
                            < / div >

                                < h2 > 无懈可击报表修改工具（密码保护版） < / h2 >

                                                                            < div


class ="input-group" >

< label > 选择需要修改的Excel报表文件: < / label > < br >
< input
type = "file"
id = "fileInput" >
< / div >

< div


class ="input-group" >

< label > 实际人数: < / label > < br >
< input
type = "number"
id = "actualPull"
min = "0" >
< / div >

< div


class ="input-group" >

< label > 清除指定数据行(逗号分隔): < / label > < br >
< input
type = "text"
id = "deleteRows" >
< / div >

< button
onclick = "handleFile()" > 开始执行 < / button >
< div
id = "status" > < / div >

< script
src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.0/xlsx.full.min.js" > < / script >
< script >
let
isPasswordVerified = false;

async function
loadPassword()
{
try {
// 带时间戳防止缓存
const response = await fetch('https://gufeng443.github.io/GF666/password.txt?t=' + Date.now());
const serverPassword = await response.text();
return serverPassword.trim() | | '147258369'; // 确保服务器返回空时使用默认密码
} catch(error)
{
return '147258369'; // 网络故障时的备用密码
}
}

async function
verifyPassword()
{
    const
userInput = document.getElementById('passwordInput').value;
const
statusElem = document.getElementById('passwordStatus');

if (!userInput)
{
statusElem.style.color = 'red';
statusElem.innerHTML = '请输入密码';
return;
}

const
serverPassword = await loadPassword();

if (userInput === serverPassword)
{
isPasswordVerified = true;
statusElem.style.color = 'green';
statusElem.innerHTML = '✓ 验证通过（有效时间60分钟）';
setTimeout(() = > {
    isPasswordVerified = false;
statusElem.innerHTML = '× 会话已过期，请重新验证';
}, 3600000); // 60
分钟后过期
} else {
isPasswordVerified = false;
statusElem.style.color = 'red';
statusElem.innerHTML = '× 密码错误';
}
}

function
modifyExcel(workbook, actualPullCount, rowsToDelete)
{
/ * 原有modifyExcel函数保持不变 * /
// ...
原有代码...
}

function
handleFile()
{
if (!isPasswordVerified)
{
document.getElementById('status').innerHTML =
'<div class="warning">请先通过密码验证！</div>';
return;
}

const
file = document.getElementById('fileInput').files[0];
const
actualPull = document.getElementById('actualPull').value;
const
deleteRows = document.getElementById('deleteRows').value;
const
statusElem = document.getElementById('status');


<script>
function modifyExcel(workbook, actualPullCount, rowsToDelete) {
    try {
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        let data = XLSX.utils.sheet_to_json(sheet, {header:1, defval:""});

        // 数据校验
        if(data.length < 5) throw new Error("文件行数不足，最少需要5行数据");

        // 处理删除行
        if(rowsToDelete.trim()) {
            const toDelete = new Set(rowsToDelete.split(',').map(Number));
            data = data.filter((row, index) => {
                if(index === 0 || index >= data.length-3) return true; // 保留标题和统计行
                const groupName = row[4] || '';
                const groupNumber = groupName.toString().split('-').pop();
                return !toDelete.has(Number(groupNumber));
            });
        }

        // 预处理数据行
        data.forEach((row, index) => {
            if(index === 0 || index >= data.length-3) return;

            // 确保数值类型
            row[0] = Number(row[0]) || 0;
            row[1] = Number(row[1]) || 0;
            row[2] = Number(row[2]) || 0;
        });

        // 更新任务数行
        let taskCountUpdated = false;
        data = data.map((row, index) => {
            const firstCell = row[0]?.toString() || '';
            if(firstCell.startsWith('任务数:')) {
                row[0] = `任务数:${data.length - 5}`;
                taskCountUpdated = true;
            }
            return row;
        });

        if(!taskCountUpdated) {
            data.push([`任务数:${data.length - 4}`]);
        }

        // 执行分配逻辑
        const validRows = data.slice(1, data.length-3).filter(row => row[0] > 0);
        let remainingPull = Number(actualPullCount);

        // 计算最大可分配值
        const maxPullable = validRows.reduce((sum, row) => sum + Math.min(row[0],4), 0);
        if(remainingPull > maxPullable) throw new Error(`实际人数超过最大可分配值(${maxPullable})`);
        if(remainingPull < 0) throw new Error("实际人数不能为负数");

        // 第一阶段分配
        validRows.sort(() => Math.random() - 0.5);
        validRows.forEach(row => {
            const maxPull = Math.min(row[0],4);
            const pull = Math.min(Math.floor(Math.random()*(maxPull-1+1)+2), remainingPull);
            row[1] = Math.min(pull, maxPull);
            row[2] = row[0] - row[1];
            remainingPull -= row[1];
        });

        // 第二阶段补充分配
        if(remainingPull > 0) {
            validRows.sort((a,b) => a[1] - b[1]).forEach(row => {
                const available = Math.min(row[0],4) - row[1];
                if(available > 0) {
                    const add = Math.min(available, remainingPull);
                    row[1] += add;
                    row[2] -= add;
                    remainingPull -= add;
                }
            });
        }

        // 更新统计信息
        const totalMember = validRows.reduce((sum,row) => sum + row[0], 0);
        const totalPull = validRows.reduce((sum,row) => sum + row[1], 0);

        // 更新统计行
        data[data.length-4] = [`总人数: ${totalMember}`, `总拉人数: ${totalPull}`];

        const newSheet = XLSX.utils.aoa_to_sheet(data);
        workbook.Sheets[workbook.SheetNames[0]] = newSheet;
        return workbook;

    } catch(e) {
        document.getElementById('status').innerHTML =
            `<div class="warning">错误: ${e.message}</div>`;
        throw e;
    }
}

function handleFile() {
    const file = document.getElementById('fileInput').files[0];
    const actualPull = document.getElementById('actualPull').value;
    const deleteRows = document.getElementById('deleteRows').value;
    const statusElem = document.getElementById('status');

    statusElem.innerHTML = "处理中...";

    if(!file || !actualPull) {
        statusElem.innerHTML = '<div class="warning">请填写全部必填项</div>';
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});

            const modifiedWB = modifyExcel(workbook, actualPull, deleteRows);
            const wbout = XLSX.write(modifiedWB, {bookType:'xlsx', type:'array'});

            // 保存文件
            const blob = new Blob([wbout], {type:"application/octet-stream"});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `modified_${new Date().getTime()}.xlsx`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            statusElem.innerHTML = "文件处理完成 ✅ 已开始下载！";
        } catch(e) {
            console.error(e);
            statusElem.innerHTML =
                `<div class="warning">处理失败: ${e.message}</div>
                 <div>请检查：1.文件格式 2.输入数值 3.控制台日志</div>`;
        }
    };
    reader.onerror = () => {
        statusElem.innerHTML = '<div class="warning">文件读取失败</div>';
    };
    reader.readAsArrayBuffer(file);
}


// 绑定回车键验证功能
document.getElementById('passwordInput').addEventListener('keypress', (e) = > {
if (e.key === 'Enter') verifyPassword();
});
< / script >
    < / body >
        < / html >
