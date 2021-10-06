import { Injectable } from '@angular/core';
import config from '../../../assets/config.json';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import axios, { AxiosResponse } from 'axios';
import { HttpClient, HttpParams } from '@angular/common/http';
import { saveAs } from 'file-saver';
@Injectable({
  providedIn: 'root',
})
export class BackendService {
  backendUrl = `${config.backendUrl}:${config.backendPort}`;
  workingFolders: string[];
  deploymentIdentifier: string;
  constructor(private http: HttpClient) {}

  async getFormTemplate(): Promise<IDomain[]> {
    try {
      const form = await axios.get(`${this.backendUrl}/deployment/form`);
      return form.data.form;
    } catch (error) {
      console.log(error);
    }
  }

  downloadOutputsFolder(identifier: string) {
    let params = new HttpParams().set('identifier', identifier);
    this.http
      .get(`${this.backendUrl}/deployment/getoutput`, {
        responseType: 'blob',
        params: params,
      })
      .toPromise()
      .then((blob) => {
        saveAs(blob, 'deployment_outpus.zip');
        axios.post(`${this.backendUrl}/deployment/deleteoutput`, {identifier: identifier})
      })
      .catch((err) => console.error('download error = ', err));
  }

  async startDeployment(form: IDomain[], deleteMode: boolean = false) {
    try {
      let result: AxiosResponse<any>;
      result = await axios.post(`${this.backendUrl}/deployment`, {
        form,
        deleteMode,
      });
      return result.data;
    } catch (error) {
      throw error;
    }
  }
}
