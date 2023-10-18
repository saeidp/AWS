import { exec } from 'node:child_process';
import * as logic from '/opt/business-logic';

export const handler = async (event: any = {}): Promise<any> => {
    console.log(`Addition:${logic.add(2, 3)}`);

    // This part is optional code to list the contents of /opt and /var/task folders
    // in /var/task index.json and in /opt logic.ts will be shown
    const commands = ['ls -R /var/task', 'ls -R /opt'];
    for (const cmd of commands) {
        try {
            const res = await execShellCommand(cmd);
            console.log(`Result of ${cmd}:`, res);
        } catch (err) {
            console.log(`error executing command - ${cmd}:`, err);
        }
    }
};

function execShellCommand(cmd: any) {
    return new Promise((resolve, reject) => {
        exec(cmd, (error: any, stdout: any, stderr: any) => {
            if (error) {
                console.warn(error);
            }
            resolve(stdout ? stdout : stderr);
        });
    });


};