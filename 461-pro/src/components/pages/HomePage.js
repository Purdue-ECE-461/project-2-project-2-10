import React, {Component} from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

export default class HomePage extends Component {
    state ={
        selectedFile: null,
        ID: '',
        name: '',
        version: '',
        URL: '',
        getID: '',
        getName: '',
        getVersion: '',
        packages: null,
        delete: ''
    };
      

    onFileChange = event => {
        this.setState({ selectedFile: event.target.files[0] });
    };




    Delete = (event) => {
        event.preventDefault();
        let headers = new Headers();

        headers.append('Access-Control-Allow-Origin', 'http://localhost:3000');
        headers.append('Access-Control-Allow-Credentials', 'true');
        
        axios.delete('http://symmetric-index-334318.uc.r.appspot.com/package', {
            params: {ID: this.state.delete}}, headers)
            .then((response) => {
                console.log(response.data.packages);
                console.log(this.state.delete);
        });
    }

    onFileDownload = (event) => {
        event.preventDefault();
        let headers = new Headers();

        headers.append('Access-Control-Allow-Origin', 'http://localhost:3000');
        headers.append('Access-Control-Allow-Credentials', 'true');

        axios.get('http://symmetric-index-334318.uc.r.appspot.com/package')
            .then((response) => {
                this.setState({packages: response.data.packages});
                console.log(response.data.packages[0].Name);
                console.log(response.data);
                console.log(response.data.packages.length);
                console.log(response.data.packages[0]);
                console.log(response.status);
                console.log(response.statusText);
                console.log(response.headers);
                console.log(response.config);
        });
        
    }
    onFileUpload = (event) => {
        event.preventDefault();
        let headers = new Headers();

        headers.append('Access-Control-Allow-Origin', 'http://localhost:3000');
        headers.append('Access-Control-Allow-Credentials', 'true');

        const formData = {
            "metadata": JSON.stringify({
              "Name": this.state.name,
              "Version": this.state.version,
              "ID": this.state.ID
            }),
            "data": JSON.stringify({
              "Content": "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",
		      "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
            })
          }

        const formDataURL = {
            "metadata": JSON.stringify({
                "Name": this.state.name,
                "Version": this.state.version,
                "ID": this.state.ID
            }),
            "data": JSON.stringify({
                "URL": this.state.URL,
                "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
            })
        }
    
        console.log(this.state.selectedFile);
    
        //axios.post("http://symmetric-index-334318.uc.r.appspot.com/package", formData);
        if(this.state.URL === ""){
            axios
                .post("http://symmetric-index-334318.uc.r.appspot.com/package", formData, headers)
                .then(res=> {
                    console.log(`statusCode: ${res.status}`)
                })
                .catch(error=> {
                    console.error(error)
                })
        }
        else{
            axios
                .post("http://symmetric-index-334318.uc.r.appspot.com/package", formDataURL, headers)
                .then(res=> {
                    console.log(`statusCode: ${res.status}`)
                })
                .catch(error=> {
                    console.error(error)
                })
        }
    };
    
    handleNameChange(event) {
        this.setState({name: event.target.value});
    }
    handleIDChange(event) {
        this.setState({ID: event.target.value});
    }
    handleVersionChange(event) {
        this.setState({version: event.target.value});
    }
    hangleURLChange(event) {
        this.setState({URL: event.target.value});
    }


    getData = () => {
        if(this.state.packages){
            var out = [];
            for(let i = 0; i < this.state.packages.length; i++){
                out.push("Package: " + i);
                out.push(<br/>);
                out.push("        Name: " + this.state.packages[i].Name);
                out.push(<br/>);
                out.push("        Version: " + this.state.packages[i].Version);
                out.push(<br/>);
                out.push("        ID: " + this.state.packages[i].ID);
                out.push(<br/>);
                out.push(<br/>);
            }
            var t = <p>hello</p>
            return(
                <div>
                    {out}
                </div>
            )
        }
        else{
            return(
                <div>
                    <p>Click Get</p>
                </div>
            )
        }
    }
    fileData = () => {
        if (this.state.selectedFile){
            return(
                <div>
                    <p>File Details:</p>
                    <p>File Name: {this.state.selectedFile.name}</p>
                    <p>File Type: {this.state.selectedFile.type}</p>
                </div>
            );
        }else{
            return (
                <div>
                    <p>Choose before pressing the "Upload" button</p>
                </div>
            );
        }
    };
    render(){
        return (
            <container>
                {/* <h1 className="main-title home-page-title">welcome to our app</h1> */}
                <form className="setVisible" style={FormStyle}>
                    <p className= "center">
                        <label>Name</label><br/>
                        <input type="text" placeholder="enter name" name="name" value={this.state.value} onChange={ev => this.setState({name: ev.target.value})} required />
                    </p>
                    <p className= "center">
                        <label>Version</label><br/>
                        <input type="text" placeholder="enter version" name="version" value={this.state.value} onChange={ev => this.setState({version: ev.target.value})} required />
                    </p>
                    <p className= "center">
                        <label>ID</label><br/>
                        <input type="text" name="ID" placeholder="enter ID" value={this.state.value} onChange={ev => this.setState({ID: ev.target.value})} required />
                    </p>
                    <p className="center">
                        <label>Github URL</label><br/>
                        <input type="text" name="URL" placeholder="enter GitHub URL" value={this.state.value} onChange={ev => this.setState({URL: ev.target.value})} />
                    </p>
                    <div className="buttons" class="inline">
                        <input type="file" onChange={this.onFileChange} />
                        <button value="Submit" onClick={this.onFileUpload}>Upload File</button>
                    </div>
                    {this.fileData()}
                </form>



                <form className="setVisible" style={FormStyle}>
                    <div className="buttons" class="center">
                        <button className="home-button" onClick={this.onFileDownload}>Get</button>
                    </div>
                    {this.getData()}
                </form>


                <form className="setVisible" style={FormStyle}>
                    <div className="buttons" class="center">
                        <label>Delete Package ID</label><br/>
                        <input type="text" placeholder="enter ID" name="delete" value={this.state.value} onChange={ev => this.setState({delete: ev.target.value})} required />
                        <button className="home-button" onClick={this.Delete}>Delete</button>
                    </div>
                </form>


                <div className="buttons" class="inline">
                    <button className="home-button">Update</button>
                    <button className="home-button">Rate</button>
                </div>
                
                <Link to="/" className="center">
                    <button className="logout-button">Log out</button>
                </Link>
            </container>
        )
    }
}

const FormStyle = {
    width: "400px",
    maxheight: "350px",
}
