import { MessageHandlerService } from '../message-handler/message-handler.service';
import { IS3Bucket } from '../../interfaces/client/IS3';
import { Injectable } from '@angular/core';
import * as AWS from 'aws-sdk/global';
import S3 from 'aws-sdk/clients/s3';
import { IDomain } from '../../interfaces/common/IDomain';
@Injectable({
  providedIn: 'root',
})
export class S3Service {
  private readonly storageName = 's3-credentials';
  private credentials: IS3Bucket;
  private bucket: S3;
  constructor(private errorHandlerService: MessageHandlerService) {}

  public async setCredentials(s3Info: IS3Bucket): Promise<boolean> {
    AWS.config.credentials = new AWS.Credentials({
      accessKeyId: s3Info.accessKeyId,
      secretAccessKey: s3Info.secretAccessKey,
    });
    AWS.config.update({ region: s3Info.region });
    const result = await this.verifyCredentials(s3Info);
    if (result) {
      if (s3Info.storeCredentials) {
        localStorage.setItem(this.storageName, JSON.stringify(s3Info));
      }
      this.credentials = s3Info;
    }
    return result;
  }

  private async verifyCredentials(bucketInfo: IS3Bucket): Promise<boolean> {
    try {
      this.bucket = this.getBucket(bucketInfo.bucketName);
      await this.listDeploymentFiles(bucketInfo);
      this.credentials = bucketInfo;
      return true;
    } catch (error) {
      this.errorHandlerService.onErrorOccured.next(
        `failed to connect to bucket: ${error.message} `
      );
      return false;
    }
  }

  public async isCredentialsLoaded(): Promise<boolean> {
    const fromStorage = JSON.parse(
      localStorage.getItem(this.storageName)
    ) as IS3Bucket;
    if (!fromStorage || !(await this.setCredentials(fromStorage))) {
      return false;
    }
    return true;
  }

  public clearCredentials() {
    localStorage.removeItem(this.storageName);
  }

  private getBucket(bucketName: string): S3 {
    const s3 = new S3({
      apiVersion: '2006-03-01',
      params: { Bucket: bucketName },
    });
    return s3;
  }

  public async listDeploymentFiles(bucketInfo?: IS3Bucket): Promise<string[]> {
    const bucketName = bucketInfo?.bucketName || this.credentials.bucketName;
    if (!bucketName) {
      throw 'Not authenticated';
    }
    try {
      const fileNames: string[] = [];
      const data = await this.bucket
        .listObjectsV2({
          Bucket: bucketName,
        })
        .promise();
      for (const bucketItem of data.Contents) {
        fileNames.push(bucketItem.Key);
      }

      return fileNames;
    } catch (error) {
      console.log(error);
      throw error.message;
    }
  }

  public async loadDeploymentFile(fileNmae: string): Promise<IDomain[]> {
    
    const response = await this.bucket
      .getObject({
        Bucket: this.credentials.bucketName,
        Key: fileNmae,
      })
      .promise();
    return JSON.parse(response.Body.toString());
  }

  public async uploadForm(jsonFileContent: string, fileName:string): Promise<any> {
    const uploadResult = await this.bucket
      .putObject({
        Bucket: this.credentials.bucketName,
        Key: fileName,
        Body: jsonFileContent,
      })
      .promise();
    return uploadResult;
  }
}
