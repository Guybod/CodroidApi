using System;
using System.Data;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace CodroidAPI
{
    public class Codroid : IDisposable
{
    public Codroid(string ip, int port)
    {   
        _ip = ip;
        _port = port;
        _client = new TcpClient();
    }

    public bool DEBUG;
    private TcpClient _client;
    private NetworkStream _stream;
    private bool _isConnected;
    private string _ip;
    private int _port;
    
    // 事件定义，用于状态通知
    public event Action<string> OnMessageReceived;
    public event Action<string> OnError;
    public event Action OnConnected;
    public event Action OnDisconnected;
    
    /// <summary>
    /// 获取连接状态
    /// </summary>
    public bool IsConnected => _isConnected && _client?.Connected == true;
    
    /// <summary>
    /// 连接到指定的TCP服务器
    /// </summary>
    /// <param name="timeoutMs">连接超时时间（毫秒）</param>
    /// <returns>连接是否成功</returns>
    public bool Connect(int timeoutMs = 5000)
    {
        try
        {
            if (_isConnected)
            {
                Disconnect();
            }
            
            _client = new TcpClient();
            var result = _client.BeginConnect(_ip, _port, null, null);
            var success = result.AsyncWaitHandle.WaitOne(TimeSpan.FromMilliseconds(timeoutMs));
            
            if (!success || !_client.Connected)
            {
                OnError?.Invoke("连接服务器超时");
                return false;
            }
            
            _client.EndConnect(result);
            _stream = _client.GetStream();
            _isConnected = true;
            
            OnConnected?.Invoke();
            return true;
        }
        catch (Exception ex)
        {
            OnError?.Invoke($"连接失败: {ex.Message}");
            return false;
        }
    }
    
    /// <summary>
    /// 发送消息到服务器
    /// </summary>
    /// <param name="message">要发送的消息内容</param>
    /// <returns>发送是否成功</returns>
    private bool SendMessage(string message)
    {
        if (!IsConnected)
        {
            OnError?.Invoke("未连接到服务器，无法发送消息");
            return false;
        }
        
        try
        {
            byte[] dataToSend = Encoding.UTF8.GetBytes(message);
            _stream.Write(dataToSend, 0, dataToSend.Length);
            return true;
        }
        catch (Exception ex)
        {
            OnError?.Invoke($"发送消息失败: {ex.Message}");
            _isConnected = false;
            return false;
        }
    }
    
    /// <summary>
    /// 接收服务器消息（同步方式）
    /// </summary>
    /// <param name="timeoutMs">接收超时时间（毫秒）</param>
    /// <returns>接收到的消息内容，超时或失败返回null</returns>
    private string ReceiveMessage(int timeoutMs = 5000)
    {
        if (!IsConnected)
        {
            OnError?.Invoke("未连接到服务器，无法接收消息");
            return null;
        }
        
        try
        {
            byte[] buffer = new byte[1024];
            _stream.ReadTimeout = timeoutMs;
            
            int bytesRead = _stream.Read(buffer, 0, buffer.Length);
            if (bytesRead > 0)
            {
                string receivedData = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                OnMessageReceived?.Invoke(receivedData);
                return receivedData;
            }
        }
        catch (Exception ex)
        {
            OnError?.Invoke($"接收消息失败: {ex.Message}");
            _isConnected = false;
        }
        
        return null;
    }
    
    /// <summary>
    /// 静态方法，将string转换为JsonObject
    /// </summary>
    /// <param name="jsonString"></param>
    /// <returns></returns>
    /// <exception cref="ArgumentException"></exception>
    private static JsonObject SafeStringToJsonObject(string jsonString)
    {
        if (string.IsNullOrWhiteSpace(jsonString))
        {
            throw new ArgumentException("JSON字符串不能为空");
        }
    
        try
        {
            JsonNode node = JsonNode.Parse(jsonString);
        
            if (node == null)
            {
                throw new ArgumentException("无效的JSON格式");
            }
        
            JsonObject jsonObject = node.AsObject();
            return jsonObject;
        }
        catch (JsonException ex)
        {
            throw new ArgumentException($"JSON解析失败: {ex.Message}", ex);
        }
    }
    
    
    /// <summary>
    /// 发送消息并等待响应
    /// </summary>
    /// <param name="id"></param>
    /// <param name="type"></param>
    /// <param name="data"></param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    private string SendAndReceiveJson(int id, string type, JsonNode data, int timeoutMs = 5000)
    {
        var json = new JsonObject
        {
            ["id"] = id,
            ["ty"] = type,
            ["db"] = data
        };
        
        string jsonString = json.ToJsonString();
        if (DEBUG)
        {
            Console.WriteLine("发送消息：" + jsonString);
        }
        if (SendMessage(jsonString))
        {   
            string receiveMsg = ReceiveMessage(timeoutMs);
            if (DEBUG)
            {
                Console.WriteLine("接收消息：" + receiveMsg);
            }
            return receiveMsg;
        }
        return null;
    }
    
    /// <summary>
    /// 发送消息并等待响应
    /// </summary>
    /// <param name="id"></param>
    /// <param name="type"></param>
    /// <param name="data"></param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    private string SendAndReceiveJson(int id, string type, int data, int timeoutMs = 5000)
    {
        var json = new JsonObject
        {
            ["id"] = id,
            ["ty"] = type,
            ["db"] = data
        };
        
        string jsonString = json.ToJsonString();
        if (DEBUG)
        {
            Console.WriteLine("发送消息：" + jsonString);
        }
        if (SendMessage(jsonString))
        {
            string receiveMsg = ReceiveMessage(timeoutMs);
            if (DEBUG)
            {
                Console.WriteLine("接收消息：" + receiveMsg);
            }
            return receiveMsg;
        }
        return null;
    }
    
    /// <summary>
    /// 发送消息并等待响应
    /// </summary>
    /// <param name="id"></param>
    /// <param name="type"></param>
    /// <param name="data"></param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    private string SendAndReceiveJson<T>(int id, string type, T[] data, int timeoutMs = 5000)
    {
        var json = new JsonObject
        {
            ["id"] = id,
            ["ty"] = type,
            ["db"] = JsonSerializer.SerializeToNode(data)
        };
        
        string jsonString = json.ToJsonString();
        if (DEBUG)
        {
            Console.WriteLine("发送消息：" + jsonString);
        }
        if (SendMessage(jsonString))
        {
            string receiveMsg = ReceiveMessage(timeoutMs);
            if (DEBUG)
            {
                Console.WriteLine("接收消息：" + receiveMsg);
            }
            return receiveMsg;
        }
        return null;
    }
    
    
    /// <summary>
    /// 断开与服务器的连接
    /// </summary>
    public void Disconnect()
    {
        try
        {
            _stream?.Close();
            _client?.Close();
        }
        catch (Exception ex)
        {
            OnError?.Invoke($"断开连接时发生错误: {ex.Message}");
        }
        finally
        {
            _isConnected = false;
            OnDisconnected?.Invoke();
        }
    }

    /// <summary>
    /// 运行脚本
    /// </summary>
    /// <param name="mainProgram">主程序</param>
    /// <param name="subThreadsName">线程名</param>
    /// <param name="subThreads">线程</param>
    /// <param name="subProgramsName">子程序名</param>
    /// <param name="subPrograms">子程序</param>
    /// <param name="interruptsName">中断程序名</param>
    /// <param name="interrupts">中断程序</param>
    /// <param name="vars">变量Json格式</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject RunScript(string mainProgram, string subThreadsName = null, string subThreads = null,
        string subProgramsName = null, string subPrograms = null, string interruptsName = null,
        string interrupts = null, JsonObject vars = null, int id = 1,int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject scripts = new JsonObject();
        scripts["main"] = mainProgram;
        if (subThreadsName != null && subThreads != null)
            scripts[subThreadsName] = subThreads;
        if (subProgramsName != null && subPrograms != null)
            scripts[subProgramsName] = subPrograms;
        if (interruptsName != null && interrupts != null)
            scripts[interruptsName] = interrupts;
        data["scripts"] = scripts;
        data["vars"] = vars ;
        
        string message = SendAndReceiveJson(id, "project/runScript", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 进入远程脚本模式
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject EnterRemoteScriptMode(int id= 1,int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/enterRemoteScriptMode", data,timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 运行工程
    /// </summary>
    /// <param name="id">id</param>
    /// <param name="projectId">工程ID</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject RunProject(string projectId, int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        data["id"] = projectId;
        string message = SendAndReceiveJson(id, "project/run", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 通过工程映射索引号运行工程
    /// </summary>
    /// <param name="index">索引号</param>
    /// <param name="id">id</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject RunProjectByIndex(int index, int id = 1, int timeoutMs = 5000)
    {
        string message = SendAndReceiveJson(id, "project/runByIndex", index, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 单步运行
    /// </summary>
    /// <param name="projectId">项目ID</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject RunStep(string projectId = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        data["id"] = projectId;
        string message = SendAndReceiveJson(id, "project/runStep", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 暂停工程
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject PauseProject(int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/pause", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 恢复运行工程
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject ResumeProject(int id = 1, int timeoutMs = 5000)
    { 
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/resume", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }

    /// <summary>
    /// 停止运行工程
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject StopProject(int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/stop", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }

    /// <summary>
    /// 设置断点
    /// </summary>
    /// <param name="projectId">工程ID</param>
    /// <param name="lineNumber">断点行号列表</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetBreakpoint(string projectId, int[] lineNumber, int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        data[projectId] = JsonSerializer.SerializeToNode(lineNumber);
        string message = SendAndReceiveJson(id, "project/setBreakpoint", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 添加断点
    /// </summary>
    /// <param name="projectId">工程ID</param>
    /// <param name="lineNumber">断点行号列表</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject AddBreakpoint(string projectId, int[] lineNumber, int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        data[projectId] = JsonSerializer.SerializeToNode(lineNumber);
        string message = SendAndReceiveJson(id, "project/addBreakpoint", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 删除断点
    /// </summary>
    /// <param name="projectId">工程ID</param>
    /// <param name="lineNumber">断点行号列表</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    private JsonObject RemoveBreakpoint(string projectId, int[] lineNumber, int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        data[projectId] = JsonSerializer.SerializeToNode(lineNumber);
        string message = SendAndReceiveJson(id, "project/removeBreakpoint", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 清除所有断点
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject ClearBreakpoint(int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/clearBreakpoint", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 设置启动行
    /// </summary>
    /// <param name="startline">起始行号</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetStartLine(int startline, int id = 1, int timeoutMs = 5000)
    {
        string message = SendAndReceiveJson(id, "project/setStartLine", startline, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 清除从指定行运行
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject ClearStartLine(int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "project/clearStartLine", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 获取全局变量
    /// </summary>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject GetGlobalVars(int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        string message = SendAndReceiveJson(id, "globalVar/getVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 保存全局变量
    /// </summary>
    /// <param name="name">变量名</param>
    /// <param name="value">变量值</param>
    /// <param name="note">注释</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetGlobalVar(string name, string value, string note = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject valueAndNm = new JsonObject();
        valueAndNm["val"] = value;
        valueAndNm["nm"] = note;
        data[name] = valueAndNm;
        string message = SendAndReceiveJson(id, "globalVar/saveVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 保存全局变量
    /// </summary>
    /// <param name="name">变量名</param>
    /// <param name="value">变量值</param>
    /// <param name="note">注释</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetGlobalVar(string name, int value, string note = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject valueAndNm = new JsonObject();
        valueAndNm["val"] = value.ToString();
        valueAndNm["nm"] = note;
        data[name] = valueAndNm;
        string message = SendAndReceiveJson(id, "globalVar/saveVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 保存全局变量
    /// </summary>
    /// <param name="name">变量名</param>
    /// <param name="value">变量值</param>
    /// <param name="note">注释</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetGlobalVar(string name, double value, string note = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject valueAndNm = new JsonObject();
        valueAndNm["val"] = value.ToString();
        valueAndNm["nm"] = note;
        data[name] = valueAndNm;
        string message = SendAndReceiveJson(id, "globalVar/saveVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 保存全局变量
    /// </summary>
    /// <param name="name">变量名</param>
    /// <param name="value">变量值数组</param>
    /// <param name="note">注释</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// 
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetGlobalVar<T>(string name, T[] value, string note = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject valueAndNm = new JsonObject();
        StringBuilder sb = new StringBuilder();
        sb.Append("[");
        for (int i = 0; i < value.Length; i++)
        {
            sb.Append(value[i]);
            if (i < value.Length - 1)
                sb.Append(",");
        }
        sb.Append("]");
        string result = sb.ToString();
        valueAndNm["val"] = result;
        valueAndNm["nm"] = note;
        data[name] = valueAndNm;
        string message = SendAndReceiveJson(id, "globalVar/saveVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }
    
    /// <summary>
    /// 保存全局变量
    /// </summary>
    /// <param name="name">变量名</param>
    /// <param name="value">变量值数组</param>
    /// <param name="note">注释</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject SetGlobalVar(string name, JsonObject value, string note = "", int id = 1, int timeoutMs = 5000)
    {
        JsonObject data = new JsonObject();
        JsonObject valueAndNm = new JsonObject();
        string jsonString = value.ToJsonString();
        valueAndNm["val"] = jsonString;
        valueAndNm["nm"] = note;
        data[name] = valueAndNm;
        string message = SendAndReceiveJson(id, "globalVar/saveVars", data, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }


    /// <summary>
    /// 删除全局变量
    /// </summary>
    /// <param name="names">变量名数组</param>
    /// <param name="id">请求ID，默认为1</param>
    /// <param name="timeoutMs">等待响应的超时时间</param>
    /// <returns>服务器的响应内容</returns>
    public JsonObject RemoveGlobalVars(string[] names, int id = 1, int timeoutMs = 5000)
    {
        string message = SendAndReceiveJson(id, "globalVar/removeVars", names, timeoutMs);
        if (message != null)
        {
            JsonObject messageJson = SafeStringToJsonObject(message);
            return messageJson ;
        }
        return null;
    }

        /// <summary>
        /// 获取工程变量
        /// </summary>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject GetProjectVars(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "globalVar/GetProjectVarUpdate", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// RS485初始化
        /// </summary>
        /// <param name="baud_rate">波特率</param>
        /// <param name="stop_bit">停止位</param>
        /// <param name="data_bit">数据位</param>
        /// <param name="parityint">校验位，0-无校验，1-奇校验，2-偶校验 默认0</param>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject RS485Init(int baud_rate = 115200, int stop_bit = 1,int data_bit = 8 ,int parityint = 0,int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            data["baud_rate"] = baud_rate;
            data["stop_bit"] = stop_bit;
            data["data_bit"] = data_bit;
            data["parity"] = parityint;
            string message = SendAndReceiveJson(id, "EC2RS485/init", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// 清空RS485读缓冲区
        /// </summary>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject RS485FlushReadBuffer(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "EC2RS485/flushReadBuffer", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// RS485读取数据
        /// </summary>
        /// <param name="length">要读取的数据长度</param>
        /// <param name="timeout">超时时间（毫秒），默认3000</param>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject RS485Read(int length, int timeout = 3000, int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            data["length"] = length;
            data["timeout"] = timeout;
            string message = SendAndReceiveJson(id, "EC2RS485/read", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="hexString">要写入的十进制数组（对应 hex）</param>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject RS485Write(int[] hexString, int id = 1, int timeoutMs = 5000)
        {
            string message = SendAndReceiveJson(id, "EC2RS485/write", hexString, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// 创建Tcp设备
        /// </summary>
        /// <param name="devicename">设备名称,唯一值</param>
        /// <param name="ip">设备IP地址</param>
        /// <param name="port">设备端口号</param>
        /// <param name="slavedId">从机地址</param>
        /// <param name="endian">字节序：1-大端，2-小端，默认1</param>
        /// <param name="id">请求ID，默认为1</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject SetModbusTcpDevice(string devicename, string ip, int port, int slavedId = 1, int endian = 1, int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            data["name"] = devicename;
            data["ip"] = ip;
            data["port"] = port;
            data["slavedId"] = slavedId;
            data["endian"] = endian;
            string message = SendAndReceiveJson(id, "ModbusTcp/setDevice", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// 机器人上使能
        /// </summary>
        /// <param name="id">id</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject SwitchOn(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "Robot/switchOn", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }
    
        /// <summary>
        /// 机器人下使能
        /// </summary>
        /// <param name="id">id</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject SwitchOff(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "Robot/switchOff", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }
    
        /// <summary>
        /// 切换到手动模式
        /// </summary>
        /// <param name="id">id</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject ToManual(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "Robot/toManual", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }

        /// <summary>
        /// 切换到自动模式
        /// </summary>
        /// <param name="id">id</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject ToAuto(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "Robot/toAuto", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }
    
        /// <summary>
        /// 切换到远程模式
        /// </summary>
        /// <param name="id">id</param>
        /// <param name="timeoutMs">等待响应的超时时间</param>
        /// <returns>服务器的响应内容</returns>
        public JsonObject ToRemote(int id = 1, int timeoutMs = 5000)
        {
            JsonObject data = new JsonObject();
            string message = SendAndReceiveJson(id, "Robot/toRemote", data, timeoutMs);
            if (message != null)
            {
                JsonObject messageJson = SafeStringToJsonObject(message);
                return messageJson;
            }
            return null;
        }
    

    
        /// <summary>
        /// 释放资源
        /// </summary>
        public void Dispose()
        {
            Disconnect();
            _stream?.Dispose();
            _client?.Dispose();
        }
    }
}
