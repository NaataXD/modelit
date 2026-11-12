using UnityEngine;
using UnityEditor;
using System.IO;
using UnityEditor.Animations;

public static class RedCrewmateSetup
{
    const string Folder = "Assets/RedCrewmate";

    [MenuItem("Tools/Red Crewmate/Create Prefab")]
    public static void CreatePrefab()
    {
        var importer = AssetImporter.GetAtPath(Folder + "/RedCrewmate.fbx") as ModelImporter;
        if (importer)
        {
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.importAnimation = true;
            var clips = importer.defaultClipAnimations;
            foreach (var clip in clips) clip.loopTime = true;
            importer.clipAnimations = clips;
            importer.SaveAndReimport();
        }
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(Folder + "/RedCrewmate.fbx");
        if (!model) { Debug.LogError("RedCrewmate.fbx puuttuu kansiosta " + Folder); return; }
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (!shader) shader = Shader.Find("HDRP/Lit");
        if (!shader) shader = Shader.Find("Standard");
        if (!shader) { Debug.LogError("Sopivaa Lit-shaderia ei löydy."); return; }
        var red = Material("Suit_Red", Color.white, .22f, shader);
        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(Folder + "/Suit_BaseColor.png");
        red.color = Color.white;
        if (red.HasProperty("_BaseMap")) red.SetTexture("_BaseMap", texture);
        if (red.HasProperty("_BaseColorMap")) red.SetTexture("_BaseColorMap", texture);
        if (red.HasProperty("_MainTex")) red.SetTexture("_MainTex", texture);
        var rubber = Material("Visor_Rubber", new Color(.025f,.03f,.04f), .15f, shader);
        var blue = Material("Visor_Blue", new Color(.38f,.73f,.9f), .7f, shader);
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
        instance.name = "RedCrewmate";
        foreach (var renderer in instance.GetComponentsInChildren<Renderer>())
        {
            renderer.sharedMaterial = renderer.name == "Visor" ? blue : renderer.name == "Visor_Rim" ? rubber : red;
        }
        var collider = instance.AddComponent<CapsuleCollider>();
        collider.center = new Vector3(0, 1, 0);
        collider.height = 2;
        collider.radius = .51f;
        var animator = instance.GetComponent<Animator>();
        if (!animator) animator = instance.AddComponent<Animator>();
        const string controllerPath = Folder + "/RedCrewmate.controller";
        var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
        if (!controller)
        {
            controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
            controller.AddParameter("Walking", AnimatorControllerParameterType.Bool);
            AnimationClip idle = null, walk = null;
            foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(Folder + "/RedCrewmate.fbx"))
            {
                var clip = asset as AnimationClip;
                if (!clip || clip.name.StartsWith("__preview__")) continue;
                if (clip.name.Contains("Idle")) idle = clip;
                if (clip.name.Contains("Walk")) walk = clip;
            }
            var machine = controller.layers[0].stateMachine;
            var idleState = machine.AddState("Idle"); idleState.motion = idle;
            var walkState = machine.AddState("Walk"); walkState.motion = walk;
            machine.defaultState = idleState;
            var start = idleState.AddTransition(walkState); start.hasExitTime = false; start.duration = .12f;
            start.AddCondition(AnimatorConditionMode.If, 0, "Walking");
            var stop = walkState.AddTransition(idleState); stop.hasExitTime = false; stop.duration = .12f;
            stop.AddCondition(AnimatorConditionMode.IfNot, 0, "Walking");
        }
        animator.runtimeAnimatorController = controller;
        animator.applyRootMotion = false;
        PrefabUtility.SaveAsPrefabAsset(instance, Folder + "/RedCrewmate.prefab");
        Object.DestroyImmediate(instance);
        AssetDatabase.SaveAssets();
        Selection.activeObject = AssetDatabase.LoadAssetAtPath<GameObject>(Folder + "/RedCrewmate.prefab");
        Debug.Log("RedCrewmate.prefab luotu. Vedä se sceneen.");
    }

    static Material Material(string name, Color color, float smoothness, Shader shader)
    {
        string path = Folder + "/" + name + ".mat";
        var result = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (result) return result;
        result = new Material(shader) { name = name, color = color };
        if (result.HasProperty("_Smoothness")) result.SetFloat("_Smoothness", smoothness);
        if (result.HasProperty("_Glossiness")) result.SetFloat("_Glossiness", smoothness);
        AssetDatabase.CreateAsset(result, path);
        return result;
    }
}
